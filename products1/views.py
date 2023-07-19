from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.generic import DetailView, ListView
import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from .models import Price, Product, PaymentHistory
from .tasks import send_payment_confirmation_email
from django.shortcuts import get_object_or_404


from django.core.mail import send_mail

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class ProductListView(ListView):
    model = Product
    context_object_name = "products"
    template_name = "products/product_list.html"

class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"
    template_name = "products/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data()
        context["prices"] = Price.objects.filter(product=self.get_object())
        return context
    

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateStripeCheckoutSessionView(View):
    """
    Create a checkout session and redirect the user to Stripe's checkout page
    """

    def post(self, request, *args, **kwargs):
        price = Price.objects.get(id=self.kwargs["pk"])
        print(request.user.email)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(price.price) * 100,
                        "product_data": {
                            "name": price.product.name,
                            "description": price.product.desc,
                            "images": [
                                f"{settings.BACKEND_DOMAIN}/{price.product.thumbnail}"
                            ],
                        },
                    },
                    "quantity": price.product.quantity,
                }
            ],
            metadata={"product_id": price.product.id},
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )
        return redirect(checkout_session.url)
    

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook view to handle checkout session completed event.
    """

    def post(self, request, format=None):
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            print("Payment successful")
            session = event["data"]["object"]
            customer_email = session["customer_details"]["email"]
            product_id = session["metadata"]["product_id"]
            product = get_object_or_404(Product, id=product_id)

            send_mail(
                subject="Here is your product",
                message=f"Thanks for your purchase. The URL is: {product.url}",
                recipient_list=[customer_email],
                from_email="your@email.com",
            )

            PaymentHistory.objects.create(
                email=customer_email, product=product, payment_status="C"
            ) # Add this


        # Can handle other events here.

        return HttpResponse(status=200)



class SuccessView(TemplateView):
     template_name = "products/success.html"
    # def get(self, request, *args, **kwargs):
    #     email = 'rasheedbabatunde76@gmail.com'
    #     subject = 'Payment Successful'
    #     message = 'Thank you for your payment.'
    #     from_email = settings.EMAIL_HOST_USER
    #     recipient_list = [email]
    #     send_mail(subject, message, from_email, recipient_list)
       

    
    #     email = 'rasheedbabatunde76@gmail.com'
    #     send_payment_confirmation_email.delay(email)
    #     return super().get(request, *args, **kwargs)


class CancelView(TemplateView):
    template_name = "products/cancel.html"