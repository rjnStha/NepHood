from flask import Flask, jsonify
from flask_cors import CORS
from DataManager import DataManager

data_Controller = DataManager()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# CORS(app, origins='http://localhost:4200') #specific origins

# Route to get a specific book by ID
@app.route('/api/company-list', methods=['GET'])
def get_list_company():
   return data_Controller.company_list()

# Route to get a specific book by ID
@app.route('/api/financial_news/<string:company>', methods=['GET'])
def get_financial_news(company):
   return data_Controller.collect_Financial_News_Data(company)

# Route to get a specific book by ID
@app.route('/api/fundamental/<string:company>', methods=['GET'])
def get_fundamental_news(company):
   return data_Controller.collect_Fundamental_Data(company)

# Route to get a specific book by ID
@app.route('/api/technical/<string:company>', methods=['GET'])
def get_technical_news(company):
   return data_Controller.collect_Technical_Data(company)

# Route to get a specific book by ID
@app.route('/api/macroeconomic', methods=['GET'])
def get_macroeconomic_news():
   return data_Controller.collect_Macroeconomic_Data()

if __name__ == '__main__':
    app.run(debug=True)