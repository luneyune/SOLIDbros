from flask import Flask, request, jsonify

app = Flask(__name__)

# Базовый endpoint
@app.route('/api/hello', methods=['GET'])
def hello_world():
    # Извлекаем параметр "name" из URL
    piska=request.args.get('piska','Guest')
    popka=request.args.get('popka','balbes')
    return jsonify({"message": f'Hello, {piska} and {popka}'})


if __name__ == '__main__':
    app.run(debug=True)