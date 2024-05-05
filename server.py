from flask import Flask, render_template, request, redirect, url_for
import pymysql
import openai
import pdfplumber
from googletrans import Translator

app = Flask(__name__)

# تنظیمات پایگاه داده MySQL
db = pymysql.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="job_application_system"
)

# تنظیمات API OpenAI
openai.api_key = "your_openai_api_key"

# تنظیمات مترجم گوگل
translator = Translator()

# مسیر اصلی
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_description = request.form['job_description']
        job_description_en = translate_to_english(job_description)
        return redirect(url_for('upload_resumes', job_description=job_description_en))
    return render_template('index.html')

# صفحه بارگذاری رزومه‌ها
@app.route('/upload_resumes', methods=['GET', 'POST'])
def upload_resumes():
    job_description = request.args.get('job_description')
    if request.method == 'POST':
        resume_files = request.files.getlist('resumes')
        if len(resume_files) > 5:
            return "Maximum of 5 resumes allowed."
        resume_ids = save_resumes_to_database(resume_files)
        evaluation_results = evaluate_resumes(job_description, resume_ids)
        return render_template('results.html', results=evaluation_results)
    return render_template('upload_resumes.html', job_description=job_description)

# ذخیره رزومه‌ها در پایگاه داده
def save_resumes_to_database(resume_files):
    resume_ids = []
    for resume_file in resume_files:
        cursor = db.cursor()
        sql = "INSERT INTO resumes (filename, data) VALUES (%s, %s)"
        cursor.execute(sql, (resume_file.filename, resume_file.read()))
        resume_id = cursor.lastrowid
        db.commit()
        cursor.close()
        resume_ids.append(resume_id)
    return resume_ids

# ارزیابی رزومه‌ها
def evaluate_resumes(job_description, resume_ids):
    evaluation_results = []
    for resume_id in resume_ids:
        cursor = db.cursor()
        sql = "SELECT filename, data FROM resumes WHERE id = %s"
        cursor.execute(sql, (resume_id,))
        resume = cursor.fetchone()
        cursor.close()

        resume_text = extract_text_from_pdf(resume[1])
        resume_text_en = translate_to_english(resume_text)

        prompt = f"Job Description: {job_description}\n\nResume: {resume_text_en}"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.7,
        )

        name, email, phone, match_percentage, summary = parse_response(response.choices[0].text)
        evaluation_results.append({
            'name': name,
            'email': email,
            'phone': phone,
            'match_percentage': match_percentage,
            'summary': summary,
            'resume_url': f"https://example.com/resumes/{resume_id}"
        })

    evaluation_results.sort(key=lambda x: x['match_percentage'], reverse=True)
    return evaluation_results

# استخراج متن از فایل PDF
def extract_text_from_pdf(pdf_data):
    with pdfplumber.open(pdf_data) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# تبدیل متن به انگلیسی
def translate_to_english(text):
    translation = translator.translate(text, dest='en')
    return translation.text

# پارس کردن پاسخ مدل زبانی
def parse_response(response_text):
    # کد برای پارس کردن پاسخ مدل زبانی و استخراج نام، ایمیل، شماره تلفن، درصد تطابق و خلاصه
    return name, email, phone, match_percentage, summary

if __name__ == '__main__':
    app.run(debug=True)
