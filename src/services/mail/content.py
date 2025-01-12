import os

def mail_content(mail_type="otp", name="", payload={}):

    frontend = os.environ.get("FRONTEND_APP", "http://127.0.0.1:3000")

    contents = {
        "email verification": {
            "subject": "Email Verification",
            "body":
            """
                <h4>Hi {name},</h4>

                <p>Use the link below to verify your email.</p>
                <a href={url} target="_blank">{url}</a>
                <br>
                <i>In case of any discrepancy kindly contact support.</i>
            """.format(name=name, url=f"{frontend}/verify-user?token={payload.get('token')}")
        },
        "password reset": {
            "subject": "Email Verification",
            "body":
            """
                <h4>Hi {name},</h4>

                <p>Use the link below to reset your password.</p>
                <a href={url} target="_blank">{url}</a>
                <br>
                <i>In case of any discrepancy kindly contact support.</i>
            """.format(name=name, url=f"{frontend}/reset-password?token={payload.get('token')}")
        },
        "otp": {
            "subject": "OTP Verification",
            "body":
            """
                <h4>Hi {name},</h4>

                <p>Use this One-Time Password for verification.</p>
                <h2>{otp}</h2>
                <i>In case of any discrepancy kindly contact support.</i>
            """.format(name=name, otp=payload.get("otp"))
        },
        "invoice": {
            "subject": "Invoice Link Creation Notification",
            "body":
            """
                <h4>Dear {name},</h4>
                <p>Content</p>
                <p>Points:</p>
                <p>1. Invoice Link Details: </p>
                <ul>
                    <li><p>Invoice number: <b>{invoice_number}</b></p></li>
                    <li><p>Date of creation: <b>{creation_date}</b></p></li>
                    <li><p>Link: <a href={invoice_link} target="_blank">{invoice_link}</a></p></li>
                </ul>
                <br>
                <br>
                <p>Best regards,</p>
                <p>{company_name}</p>
                <p>{contact_information}</p>
            """.format(name=name,
                invoice_number=payload.get("invoice_number"),
                creation_date=payload.get("creation_date"),
                invoice_link=payload.get("invoice_link"),
                company_name=payload.get("company_name"),
                contact_information=payload.get("contact_information")
            )
        },
        "payouts": {
            "subject": "Payouts Confirmation - Two-Factor Authentication Required",
            "body":
            """
                <h4>Dear {name},</h4>
                <p>Content</p>
                <p>Points:</p>
                <p>1. Enter the provided 2FA code in the designated field on the confirmation page. </p>
                <h2>{otp}</h2>
                <br>
                <br>
                <p>Best regards,</p>
                <p>{company_name}</p>
                <p>{contact_information}</p>
            """.format(name=name,
                otp=payload.get("otp"),
                company_name=payload.get("company_name"),
                contact_information=payload.get("contact_information")
            )
        },
        "scheduled transfers": {
            "subject": "Scheduled Transfers Update Confirmation - Two-Factor Authentication Required",
            "body":
            """
                <h4>Dear {name},</h4>
                <p>Content</p>
                <p>Points:</p>
                <p>1. Enter the provided 2FA code in the designated field on the confirmation page. </p>
                <h2>{otp}</h2>
                <br>
                <br>
                <p>Best regards,</p>
                <p>{company_name}</p>
                <p>{contact_information}</p>
            """.format(name=name,
                otp=payload.get("otp"),
                company_name=payload.get("company_name"),
                contact_information=payload.get("contact_information")
            )
        },
        "developer key addition": {
            "subject": "New Developer API Key Confirmation - Two-Factor Authentication Required",
            "body":
            """
                <h4>Dear {name},</h4>
                <p>Content</p>
                <p>Points:</p>
                <p>1. Enter the provided 2FA code in the designated field on the confirmation page. </p>
                <h2>{otp}</h2>
                <br>
                <br>
                <p>Best regards,</p>
                <p>{company_name}</p>
                <p>{contact_information}</p>
            """.format(name=name,
                otp=payload.get("otp"),
                company_name=payload.get("company_name"),
                contact_information=payload.get("contact_information")
            )
        }
    }

    content = contents.get(mail_type)
    if not content:
        raise ValueError("Invalid mail type.")

    return content
