from django.shortcuts import render
import razorpay
from .models import Payment as PaymentModel
from django.views.decorators.csrf import csrf_exempt

# https://razorpay.com/docs/payment-gateway/server-integration/python/usage/
# https://razorpay.com/docs/payment-gateway/web-integration/standard/
# https://razorpay.com/docs/payment-gateway/test-card-details/

def home(request):
    '''API KEYS'''
    key_id = 'PLACE YOUR PUBLIC KEY HERE'
    secret_key = 'PLACE YOUR SECRET KEY HERE'

    if request.method == 'POST':
        name = request.POST.get('name')
        product_amount = request.POST.get('amount')
        amount = int(product_amount) * 100 # 
        # API INTEGRATION
        client = razorpay.Client(auth=(key_id, secret_key))
        payment_info = client.order.create({'amount': amount, 'currency':'INR', 'payment_capture': '1'})
        print('Payment Info : ', payment_info)
        # Saving Details to Database
        payment_details = PaymentModel(name = name, amount = amount, transaction_id = payment_info['id'])
        payment_details.save()
        # Re-render to Page
        context = {'payment':payment_info, 'key_id' : key_id, 'product':name, 'amount':product_amount}
        return render(request, 'home.html', context)

    return render(request, 'home.html')


# For Fetching All POST Data from home Function.
@csrf_exempt # This decorator marks a view as being exempt from the protection ensured by the middleware.
def success(request):
    if request.method == 'POST':
        data = request.POST        
        print('Data : ', data)
        '''Payment Status Update'''
        order_id = ''
        for key, value in data.items():
            if key == 'razorpay_order_id':
                order_id = value
                break
        user = PaymentModel.objects.filter(transaction_id=order_id).first()
        user.paid = True
        user.save()
        print('Order ID : ', order_id)
    context = {}
    return render(request, 'success.html', context)