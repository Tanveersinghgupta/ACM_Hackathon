import pandas as pd
from groq import Groq

client = Groq(api_key='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')

def run_groq_model(messages, model, temperature=0.7, top_p=1, max_tokens=16):
    chat_completion = client.chat.completions.create(
        messages=messages, temperature=temperature, top_p=top_p,
        model=model, n=1, max_tokens=max_tokens
    )
    return chat_completion.choices[0].message.content

m = pd.read_csv('output_1.csv')
k = pd.read_csv('output_2.csv')
m = m.rename(columns={'Date of\nPurchase':'Date of Purchase','Bond\nNumber':'Bond Number'})
k = k.rename(columns={'Date of\nEncashment':'Date of Encashment','Bond\nNumber':'Bond Number','Pay Branch Code':'Pay Branch Code'})

frame = k.merge(m, on=['Bond Number','Prefix'], how='left', suffixes=('', '_m'))
frame.fillna(0, inplace=True)

frame['Date of Encashment'] = pd.to_datetime(frame['Date of Encashment'])
frame['Journal Date'] = pd.to_datetime(frame['Journal Date'])
frame['Date of Purchase'] = pd.to_datetime(frame['Date of Purchase'])
frame['Date of Expiry'] = pd.to_datetime(frame['Date of Expiry'])

frame['Denominations'] = frame['Denominations'].str.replace(',', '').astype(int)
frame.drop(['Denominations_m'], inplace=True, axis=1)

df=frame

def response_generator(user_input):
    question = f"""
    Question: "Write pandas code to answer the below question by carefully going through the columns and rows of the dataframe {frame}. The meaning of columns is mentioned below:
    
    'Sr No.': 'Serial number or sequence number of the entry.',
    'Date of Encashment': 'Date when the electoral bond was encashed.',
    'Name of the Political Party': 'Name of the political party receiving the electoral bond.',
    'Account no. of\nPolitical Party': 'Account number of the political party where the bond amount is deposited.',
    'Prefix': 'Prefix code for the type or category of bond.',
    'Bond Number': 'Unique identification number assigned to the electoral bond.',
    'Denominations': 'Face value or denomination of the electoral bond in Indian Rupees.',
    'Pay Branch\nCode': 'Branch code of the bank where the bond was encashed.',
    'Pay Teller': 'Name or identifier of the teller who processed the bond encashment.',
    'Reference No (URN)': 'Unique Reference Number assigned to the transaction.',
    'Journal Date': 'Date when the transaction was recorded in the bank\'s journal.',
    'Date of Purchase': 'Date when the electoral bond was purchased by the buyer.',
    'Date of Expiry': 'Date when the electoral bond expires or becomes invalid if not used.',
    'Name of the Purchaser': 'Name of the individual or entity purchasing the electoral bond.',
    'Issue Branch Code': 'Branch code of the bank that issued the electoral bond.',
    'Issue Teller': 'Name or identifier of the teller who issued the electoral bond.',
    'Status': 'Current status or state of the electoral bond (e.g., encashed, expired, etc.)'
    
    Also keep in mind that these are the Party names in the frame:-
    ['ALL INDIA ANNA DRAVIDA MUNNETRA KAZHAGAM',
       'BHARAT RASHTRA SAMITHI', 'BHARATIYA JANATA PARTY',
       'PRESIDENT, ALL INDIA CONGRESS COMMITTEE', 'SHIVSENA',
       'TELUGU DESAM PARTY',
       'YSR CONGRESS PARTY (YUVAJANA SRAMIKA RYTHU CONGRESS PARTY)',
       'DRAVIDA MUNNETRA KAZHAGAM (DMK)', 'JANATA DAL ( SECULAR )',
       'NATIONALIST CONGRESS PARTY MAHARASHTRA PRADESH',
       'ALL INDIA TRINAMOOL CONGRESS', 'BIHAR PRADESH JANTA DAL(UNITED)',
       'RASHTRIYA JANTA DAL', 'AAM AADMI PARTY',
       'ADYAKSHA SAMAJVADI PARTY', 'SHIROMANI AKALI DAL',
       'JHARKHAND MUKTI MORCHA', 'JAMMU AND KASHMIR NATIONAL CONFERENCE',
       'BIJU JANATA DAL', 'GOA FORWARD PARTY',
       'MAHARASHTRAWADI GOMNTAK PARTY', 'SIKKIM KRANTIKARI MORCHA',
       'JANASENA PARTY', 'SIKKIM DEMOCRATIC FRONT']
       
    make a match for the party name mentioned in the question and select the most suitable party name from the
    above list wherever necessary
    {user_input}
    
    Your response should be a code to be executed in '''  ''' and return just the final answer.
    """
    prompt = """
    You are an expert in the Pandas Python library. Your goal is to answer the question by generating code for the dataframe mentioned in the question.
    The question is...

    Question: """ + question

    ret = run_groq_model([{'role': 'user', 'content': prompt}], "llama3-70b-8192", max_tokens=2048, temperature=0.0)
    return ret


def code(frame, text):
    df = frame
    start_pos = text.find('```')
    end_pos = text.find('```', start_pos + 3)  # Start searching from position after first triple backticks
    answer = []
    if start_pos == -1 or end_pos == -1:
        raise ValueError("Code block not found in the text")
    
    code_block = text[start_pos + 3:end_pos].strip()

    # Create a local context dictionary
    local_vars = {'df': df}

    # Execute the code block within the provided local context
    exec(code_block, {}, local_vars)

    # Add any variables from the local context to the answer list
    for var in local_vars:
        if var != 'df':  # Exclude the input variable 'df'
            answer.append(local_vars[var])
    
    return answer[-1]

frame=df

def main(input_text_path):
    with open(input_text_path, 'r') as file:
        questions = file.readlines()
    
    processed_answers = [
        str(code(df, response_generator(question)))
        for question in questions
    ]
    print(processed_answers)
    
    output_text = './answer.txt'
    with open(output_text, 'w') as file:
        for answer in processed_answers:
            print(type(answer))
            print(answer)
            file.write(str(answer) + '\n')
    
    return output_text

main('questions.txt')