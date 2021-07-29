from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.db import transaction
from django.db.models import Sum, Q
from django.core.mail import EmailMessage
from django.urls import reverse
from .models import Cuenta, Transaccion, Cliente
from datetime import datetime
from .forms import ClienteForm

def home(request):
    if request.is_ajax() and request.method == 'POST':
        accion = request.POST.get('cbo-transaccion')

        if accion == '1': # deposito
            cuenta_id = request.POST.get('cbo-cuenta')
            monto = int(request.POST.get('txt-monto'))

            if monto <= 0:
                return JsonResponse({'color': 'warn', 'msj': 'El monto ingresado no es valido'})


            # para que los cambios sean permanentes se aplica: commit
            # para deshacer los cambios por algun error se aplica: rollback

            with transaction.atomic():
                try:
                    # Crear el objeto cuenta
                    cuenta = Cuenta.objects.get(pk=cuenta_id)

                    if not cuenta.estado:
                        return JsonResponse({'color': 'warn', 'msj': 'La cuenta a la que desea depositar está inactiva'})

                    # Depositar el monto en la cuenta
                    cuenta.saldo += float(monto)
                    cuenta.save()

                    #raise Exception('Este es un error provocado intencionalmente')

                    # Registrar el movimiento en Transaccion
                    Transaccion.objects.create(
                        movimiento = '1', # Deposito
                        origen = cuenta,
                        monto = float(monto)
                    )

                    # Enviar el correo
                    if cuenta.cliente.correo:
                        try:
                            hoy = datetime.now().strftime("%d/%m/%Y %I:%M %p")

                            body = f'''
                            Hola {cuenta.cliente}, te confirmamos que se ha hecho un depósito a tu cuenta #{cuenta.id}
                            por un monto de L{float(monto):,}.

                            Fecha de la transaccion: {hoy}
                            '''
                            
                            correo = EmailMessage('Django - Notificación de depósito', body, 'info@finapp.com', [cuenta.cliente.correo])
                            #correo.attach_file('ruta/del/archivo.pdf')
                            correo.send()
                        except:
                            pass

                    return JsonResponse({'color': 'success', 'msj': f'El deposito ha sido realizado: Saldo actual: {cuenta.saldo}'})
                
                except Exception as e:
                    return JsonResponse({'color': 'error', 'msj': str(e)})


        elif accion == '2': # retiro
            cuenta_id = request.POST.get('cbo-cuenta')
            monto = int(request.POST.get('txt-monto'))

            # if monto <= 0:
            #     return JsonResponse({'color': 'warn', 'msj': 'El monto ingresado no es valido'})


            # para que los cambios sean permanentes se aplica: commit
            # para deshacer los cambios por algun error se aplica: rollback

            with transaction.atomic():
                try:
                    # Crear el objeto cuenta
                    cuenta = Cuenta.objects.get(pk=cuenta_id)

                    # Verificar que la cuenta no esta activa
                    if not cuenta.estado:
                        return JsonResponse({'color': 'warn', 'msj': 'La cuenta a la que desea depositar está inactiva'})

                    # Verificar que la cuenta tenga saldo suficiente
                    # if cuenta.saldo < monto:
                    #     return JsonResponse({'color': 'warn', 'msj': f'La cuenta no tiene saldo suficiente. Saldo actual: {cuenta.saldo:,}'})


                    # Depositar el monto en la cuenta
                    cuenta.saldo -= float(monto)
                    cuenta.save()

                    #raise Exception('Este es un error provocado intencionalmente')

                    # Registrar el movimiento en Transaccion
                    Transaccion.objects.create(
                        movimiento = '2',
                        origen = cuenta,
                        monto = float(monto)
                    )

                    tag = ''
                    if cuenta.cliente.correo:
                        try:
                            hoy = datetime.now().strftime("%d/%m/%Y %I:%M %p")

                            body = f'''
                            Hola {cuenta.cliente}, te confirmamos que se ha realizado un retiro en tu cuenta #{cuenta.id}
                            por un monto de L{float(monto):,}.

                            Fecha de la transacción: {hoy}
                            '''
                            
                            correo = EmailMessage('Django - Notificación de retiro', body, 'info@finapp.com', [cuenta.cliente.correo])
                            #correo.attach_file('ruta/del/archivo.pdf')
                            correo.send()
                            tag = 'Correo enviado'
                        except:
                            tag = 'No se pudo enviar el correo'

                    return JsonResponse({'color': 'success', 'msj': f'El retiro ha sido realizado con éxito ({tag})'})
                
                except Exception as e:
                    return JsonResponse({'color': 'error', 'msj': str(e)})

        
        else: # transferencia
            pass

    # GET
    cuentas = Cuenta.objects.all()

    if not request.user.is_superuser:
        cuentas_propias = Cuenta.objects.filter(cliente=request.user.cliente, estado=True)
    else:
        cuentas_propias = None

    ctx = {
        'cuentas': cuentas,                     # es para el super user
        'cuentas_propias': cuentas_propias,     # es para el cliente
    }
    
    return render(request, 'banco/index.html', ctx)


def transferencias_view(request):
    if request.is_ajax() and request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'confirmar':
            # import pdb; pdb.set_trace()

            destino_id = request.POST.get('cuenta-destino')
            monto = float(request.POST.get('monto'))
            comentario = request.POST.get('comentario')

            # Consultar la cuenta destino por medio de su ID
            cuenta_destino = Cuenta.objects.filter(id=destino_id).first()

            info = ''

            if cuenta_destino:
                color = 'success'
                info = f'''
                    <table class="table table-borderless">
                        <tr>
                            <td>Cliente</td>
                            <td>{cuenta_destino.cliente}</td>
                        </tr>

                        <tr>
                            <td>Monto</td>
                            <td>{monto:,}</td>
                        </tr>

                        <tr>
                            <td>Comentarios</td>
                            <td>{comentario}</td>
                        </tr>
                    </table>
                '''
            else:
                info = 'El número de cuenta destino no existe'
                color = 'error'


            return JsonResponse({'color': color, 'msj': info})

        else: # finalizar
            destino_id = request.POST.get('cuenta-destino')
            origen_id  = request.POST.get('cuenta-origen')
            monto = float(request.POST.get('monto'))
            comentario = request.POST.get('comentario')

            # Consultar la cuenta destino por medio de su ID
            cuenta_destino = Cuenta.objects.filter(id=destino_id).first()

            # cuenta origen
            cuenta_origen = Cuenta.objects.filter(id=origen_id).first()

            # validando que ambas cuentas existan
            if cuenta_destino and cuenta_origen:
                # validar que la cuenta origen tenga saldo suficiente
                if cuenta_origen.saldo < monto:
                    OK, msj = False, 'La cuenta no tiene suficiente saldo para realizar la transferencia'
                    return JsonResponse({'OK': OK, 'msj': msj})
            
                # validar que la cuenta destino esta activa
                if not cuenta_destino.estado:
                    OK, msj = False, 'No se puede realizar la transferencia a la cuenta destino'
                    return JsonResponse({'OK': OK, 'msj': msj})
                
                # Las validaciones pasaron, realizamos la transaccion
                try:
                    with transaction.atomic():
                        # debito en la cuenta origen
                        cuenta_origen.saldo -= monto
                        cuenta_origen.save()

                        #raise Exception('Este error es intencional')

                        # credito en la cuenta destino
                        cuenta_destino.saldo += monto
                        cuenta_destino.save()


                        # registrar el movimiento
                        Transaccion.objects.create(
                            movimiento = '3', # Transferencia
                            origen = cuenta_origen,
                            destino = cuenta_destino,
                            monto = float(monto),
                            comentario = comentario
                        )

                        # en un try
                        # enviar correo electronico a ambos clientes
                        return JsonResponse({'OK': True, 'msj': 'La transacción se realizó con éxito'})

                except Exception as e:
                    return JsonResponse({'OK': False, 'msj': str(e)})




            else:
                OK, msj = False, 'Hay error en las cuentas, por favor verifique'


            return JsonResponse({'msj': origen_id})

def historial(request):
    if request.user.is_superuser:
        if request.method == 'POST' and request.is_ajax():
            cuenta_id = request.POST.get('cbo-cuenta')
            cuenta = Cuenta.objects.get(pk=cuenta_id)

            # consultar las movimientos de la cuenta
            transacciones = Transaccion.objects.filter(Q(origen__id=cuenta_id) | Q(destino__id=cuenta_id)).order_by('-fecha')

            sum_depositos = transacciones.filter(movimiento='1').aggregate(t=Sum('monto'))['t']
            sum_retiros   = transacciones.filter(movimiento='2').aggregate(t=Sum('monto'))['t']
            saldo_actual  = sum_depositos - sum_retiros


            if not transacciones:
                html = '<div class="alert alert-danger">No hay movimientos para esta cuenta</div>'
                return JsonResponse({'html': html}) 

            tr = ''
            for trans in transacciones:
                if trans.movimiento == '1': # Depositos
                    tr += f'''
                        <tr>
                            <td>{trans.fecha}</td>
                            <td>Depósito</td>
                            <td>-</td>
                            <td class="text-success text-end">{trans.monto}</td>
                        </tr>
                    '''

                elif trans.movimiento == '2': # Retiros
                    tr += f'''
                        <tr>
                            <td>{trans.fecha}</td>
                            <td>Retiro</td>
                            <td class="text-danger text-end">{trans.monto}</td>
                            <td>-</td>
                        </tr>
                    '''

                else: # Transferencias
                    if cuenta == trans.origen:
                        # la cuenta está en el campo origen: debito por transferencia
                        tr += f'''
                            <tr>
                                <td>{trans.fecha}</td>
                                <td>Débito por tranf.</td>
                                <td class="text-danger text-end">{trans.monto}</td>
                                <td>-</td>
                            </tr>
                        '''
                    else:
                        # la cuenta está en el campo destino: credito por transferencia
                        tr += f'''
                            <tr>
                                <td>{trans.fecha}</td>
                                <td>Crédito por tranf.</td>
                                <td>-</td>
                                <td class="text-success text-end">{trans.monto}</td>
                            </tr>
                        '''

            color_saldo_actual = 'text-danger' if saldo_actual <= 0 else 'text-success'

            html = f'''
                <table class="table table-bordered table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Concepto</th>
                            <th>Débito</th>
                            <th>Crédito</th>
                        </tr>
                    </thead>
                    <tbody>{tr}</tbody>
                    <tfoot>
                        <tr>
                            <th class="table-secondary"></th>
                            <th class="table-secondary"></th>
                            <th class="table-secondary text-danger text-end">{sum_retiros}</th>
                            <th class="table-secondary text-success text-end">{sum_depositos}</th>
                        </tr>
                        <tr>
                            <th class="table-dark"></th>
                            <th colspan="3" class="table-dark text-white text-end {color_saldo_actual}">Saldo actual: {saldo_actual}</th>
                        </tr>
                    </tfoot>
                </table>
            '''

            return JsonResponse({'html': html})
    else:
        raise Http404('Not Found')
    
    
    
    # este es el metodo GET
    cuentas = Cuenta.objects.all()
    return render(request, 'banco/historial.html', {'cuentas': cuentas})

def clientes_view(request):
    id = request.GET.get('id')
    
    cliente = None
    if id:
        cliente = get_object_or_404(Cliente, pk=id)

    form = ClienteForm(instance=cliente) # instancia
    clientes = Cliente.objects.all().order_by('nombre', 'apellido')
    return render(request, 'banco/clientes.html', {'form': form, 'clientes': clientes})

def clientes_gestion(request, id = None):
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, pk=id) if id else None
        form = ClienteForm(request.POST, instance=cliente)

        # form.save() hará un update si la instancia es un objeto del cliente que se quiere actualizar
        # form.save() hará un insert si la instancia es nula (None)

        if form.is_valid():
            form.save()
            return redirect(reverse('clientes_view'))
        else:
            clientes = Cliente.objects.all().order_by('nombre', 'apellido')
            return render(request, 'banco/clientes.html', {'form': form, 'clientes': clientes})


