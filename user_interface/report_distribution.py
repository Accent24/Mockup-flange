import win32com.client as win32client


def send_report(file_path):
    list_of_recipient = []
    outlook = win32client.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)

    mail.Subject = 'Test'
    mail.To = 'AOcheretianko@alto.ae;Accent24@me.com'
    mail.Send()
