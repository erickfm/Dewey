from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
import streamlit as st
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
chat = ChatOpenAI(temperature=1, model_name='gpt-3.5-turbo')


def chatgpt(content, sys="You are a helpful assistant."):
    """Useful knowledgeable assistant. Input should be a search query."""
    messages = [
        SystemMessage(content=sys),
        HumanMessage(content=content)
    ]
    return chat(messages).content


def ask(prompt, write=False):
    response = chatgpt(prompt)
    if write:
        st.write(response)
    return response


def get_letter_prompt(company, title, skills, description, resume):
    prompt = f"""Given a company, job title, desired skills, job description, and resume, generate an effective cover letter from the applicant's resume to enhance their chances of securing an interview. 
    Company: {company}
    Job title: {title}
    Desired skills: {skills}
    Job description: {description}
    Resume: {resume}
    
    
    Cover Letter: """
    return prompt


def get_webpage_text(url):
    html = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read()
    soup = BeautifulSoup(html, features="html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = [line.strip() for line in text.splitlines()]
    chunks = [phrase.strip() for line in lines for phrase in line.split("  ")]
    text = '\n '.join([chunk for chunk in chunks if chunk])
    return text


def get_job_details_prompt(webpage_text):
    prompt = f"""Given the text from a webpage for a job post, return the company, job title, desired skills, and job description in the format given below.
    Webpage text: {webpage_text}
     
    Company: 
    Job title: 
    Desired skills: 
    Job description: """
    return prompt


def get_job_details(job_details_raw):
    company = job_details_raw.split('Company:')[1].split('Job title:')[0]
    title = job_details_raw.split('Job title:')[1].split('Desired skills:')[0]
    skills = job_details_raw.split('Desired skills:')[1].split('Job description:')[0]
    description = job_details_raw.split('Job description:')[1]

    return company, title, skills, description
