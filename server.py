from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# مسیر اصلی
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_description = request.form['job_description']
        return redirect(url_for('upload_resumes', job_description=job_description))
    return render_template('index.html')

# صفحه بارگذاری رزومه‌ها
@app.route('/upload_resumes', methods=['GET', 'POST'])
def upload_resumes():
    job_description = request.args.get('job_description')
    if request.method == 'POST':
        # شبیه‌سازی بارگذاری رزومه‌ها
        resume_files = request.files.getlist('resumes')
        if len(resume_files) > 5:
            return "Maximum of 5 resumes allowed."
        # شبیه‌سازی ارزیابی رزومه‌ها توسط LLM
        evaluation_results = simulate_llm_evaluation(job_description, resume_files)
        return render_template('results.html', results=evaluation_results)
    return render_template('upload_resumes.html', job_description=job_description)

# شبیه‌سازی ارزیابی رزومه‌ها توسط LLM
def simulate_llm_evaluation(job_description, resume_files):
    evaluation_results = []
    for resume_file in resume_files:
        # شبیه‌سازی ارزیابی رزومه توسط LLM
        match_percentage = simulate_match_percentage()
        summary = simulate_summary()
        evaluation_results.append({
            'name': resume_file.filename,
            'email': 'example@example.com',
            'phone': '+1 (555) 123-4567',
            'match_percentage': match_percentage,
            'summary': summary,
            'resume_url': '#'
        })
    return evaluation_results

# شبیه‌سازی درصد تطابق
def simulate_match_percentage():
    return f"{random.randint(60, 95)}%"

# شبیه‌سازی خلاصه رزومه
def simulate_summary():
    return "این یک خلاصه شبیه‌سازی شده از رزومه است."

if __name__ == '__main__':
    app.run(debug=True)
