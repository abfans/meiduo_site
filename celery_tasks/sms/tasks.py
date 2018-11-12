from celery_tasks.main import app
from  meiduo.utils.ytx_sdk.sendSMS import CCP


@app.task
def send_sms_code(mobile, code, expires, template_id):
    try:
        CCP.sendTemplateSMS(mobile, code, expires, template_id)
        print(code)
    except:
        return "发送失败"
