from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import numpy as np
import threading

app = Flask(__name__)
CORS(app)
model = joblib.load('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    if request.is_json:  # Check if the request contains JSON data
        data = request.get_json()  # Get the JSON data from the request
        # Assuming the JSON data contains all the required fields
        int_features = [float(data.get(key)) for key in ['attack', 'count', 'dst_host_diff_srv_rate', 
                                                        'dst_host_same_src_port_rate', 'dst_host_same_srv_rate', 
                                                        'dst_host_srv_count', 'flag', 'last_flag', 'logged_in', 
                                                        'same_srv_rate', 'serror_rate', 'service_http']]

        # Process features based on attack value (same as before)
        if int_features[0] == 0:
            f_features = [0, 0, 0] + int_features[1:]
        elif int_features[0] == 1:
            f_features = [1, 0, 0] + int_features[1:]
        elif int_features[0] == 2:
            f_features = [0, 1, 0] + int_features[1:]
        else:
            f_features = [0, 0, 1] + int_features[1:]

        # Process flag feature
        if f_features[6] == 0:
            fn_features = f_features[:6] + [0, 0] + f_features[7:]
        elif f_features[6] == 1:
            fn_features = f_features[:6] + [1, 0] + f_features[7:]
        else:
            fn_features = f_features[:6] + [0, 1] + f_features[7:]

        final_features = [np.array(fn_features)]
        predict = model.predict(final_features)

        if predict == 0:
            output = 'Normal'
        elif predict == 1:
            output = 'DOS'
        elif predict == 2:
            output = 'PROBE'
        elif predict == 3:
            output = 'R2L'
        else:
            output = 'U2R'

        return jsonify({'attack_class': output})  # Return the result as JSON response

    else:
        return jsonify({'error': 'Invalid input, JSON required'}), 400

@app.route('/results', methods=['POST'])
def results():
    data = request.get_json(force=True)
    predict = model.predict([np.array(list(data.values()))])

    if predict == 0:
        output = 'Normal'
    elif predict == 1:
        output = 'DOS'
    elif predict == 2:
        output = 'PROBE'
    elif predict == 3:
        output = 'R2L'
    else:
        output = 'U2R'

    return jsonify({'attack_class': output})

def run_nids_server():
    app.run(debug=False, port=5006)

def start_nids_server():
    flask_thread = threading.Thread(target=run_nids_server, daemon=True)
    flask_thread.start()

