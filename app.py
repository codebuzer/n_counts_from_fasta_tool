from flask import Flask, request, render_template, send_file
import pandas as pd

app = Flask(__name__)

def fasta2csv(filename):
    with open(filename, 'r') as f:
        content = f.read()
        
    lines = content.splitlines()

    IDs = []
    for i in range(len(lines)):
        if lines[i].startswith('>'):
            ID = lines[i][1:].strip()
            IDs.append(ID)
    id_ = pd.DataFrame({'ID': IDs})
    seqs = []
    for i in range(1, len(lines), 2):
        seqs.append(lines[i])
    seq = pd.DataFrame({'sequence': seqs})
    df = pd.concat([id_, seq], axis=1)
    df['length'] = df['sequence'].apply(lambda x: len(x))
    df['N_counts'] = df['sequence'].apply(lambda x: x.count('N'))
    df.to_csv(filename.split('.')[0] + '.csv')
    return df

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'fastaFile' not in request.files:
            return "No file part"
        
        file = request.files['fastaFile']

        if file.filename == '':
            return "No selected file"
        
        if not file.filename.endswith('.fasta'):
            return "Invalid file extension"

        file.save(file.filename)
        df = fasta2csv(file.filename)
        
        # Generate a response to download the processed CSV file
        csv_filename = file.filename.split('.')[0] + '.csv'
        response = send_file(csv_filename, as_attachment=True)

        return response

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
