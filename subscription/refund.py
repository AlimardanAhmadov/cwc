from celery import shared_task
from paypalrestsdk import Capture

import logging, paypalrestsdk
logging.basicConfig(level=logging.INFO)



@shared_task(bind=True, max_retries=1)
def refund_customer(self, payment_id, cost):
    print("ID:", payment_id)
    capture = Capture.find(payment_id)
    #capture = paypalrestsdk.Payment.find(payment_id)
    refund = capture.refund(
        {
            "amount": {
                "currency": "USD",
                "total": cost
            }
        }
    )

    if refund.success():
        print("Refund[%s] Success" % (refund.id))
    else:
        print("Unable to Refund")
        print(refund.error)