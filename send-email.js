require("dotenv").config();

const nodemailer = require("nodemailer");

const requiredSettings = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"];

function getSmtpConfig() {
  const missing = requiredSettings.filter((name) => !process.env[name]);
  if (missing.length) {
    throw new Error(`Missing required SMTP settings: ${missing.join(", ")}`);
  }

  return {
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT),
    secure: Number(process.env.SMTP_PORT) === 465,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASSWORD,
    },
  };
}

async function sendEmail(to) {
  const transporter = nodemailer.createTransport(getSmtpConfig());
  return transporter.sendMail({
    from: process.env.SMTP_FROM,
    to,
    subject: "Hello from Meal Planner",
    text: "This is a plain text email sent with Nodemailer.",
    html: "<p>This is an <strong>HTML email</strong> sent with Nodemailer.</p>",
  });
}

if (require.main === module) {
  const recipient = process.argv[2];
  if (!recipient) {
    console.error("Usage: npm run send-email -- recipient@example.com");
    process.exitCode = 1;
  } else {
    sendEmail(recipient)
      .then((info) => console.log(`Email sent: ${info.messageId}`))
      .catch((error) => {
        console.error(`Email could not be sent: ${error.message}`);
        process.exitCode = 1;
      });
  }
}

module.exports = { sendEmail };
