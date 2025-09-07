from tools.email_tool import EmailTool

email_tool = EmailTool()

email_tool.send_email(
    to_email="mlaaboni@gmail.com",
    subject="AI Scheduler Test",
    body="Hello! This is a test email from the AI Scheduler project.",
    html="<p><b>Hello!</b> This is a <i>test email</i> from the AI Scheduler project.</p>"
)
