from io import BytesIO

from flask import Blueprint, current_app, make_response, abort, send_file

from flask import request, jsonify, Response
import jwt
import bcrypt
import datetime
from utils import get_db_connection, token_required

# Define the blueprint for users
users_blueprint = Blueprint('users', __name__)
# Apply CORS to the blueprint

#Login API for both user and Serviceman
@users_blueprint.route('/auth', methods=['POST'])
def auth():
    username = request.json.get("username")
    password = request.json.get("password")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT pass_hash, role, user_id, full_name, approval, flag, mail FROM Users WHERE username = ?',
                   (username,))
    result = cursor.fetchone()

    result1 = None
    if result and result['role'] == "influencer":
        cursor.execute('SELECT * FROM Influencers WHERE user_id = ?', (result['user_id'],))
        result1 = cursor.fetchone()
    elif result and result['role'] == "sponsor":
        cursor.execute('SELECT * FROM Sponsors WHERE user_id = ?', (result['user_id'],))
        result1 = cursor.fetchone()

    conn.close()

    if result and bcrypt.checkpw(password.encode('utf-8'), result['pass_hash'].encode('utf-8')):
        token_payload = {
            'user_id': result['user_id'],
            'username': username,
            'role': result['role'],
            'full_name': result['full_name'],
            'approval': result['approval'],
            'flag': result['flag'],
            'mail': result['mail'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=90)
        }

        if result['role'] == 'sponsor' and result1:
            token_payload.update({
                'company_name': result1['company_name'],
                'industry': result1['industry']
            })
        elif result['role'] == 'influencer' and result1:
            token_payload.update({
                'niche': result1['niche'],
                'category': result1['category'],
                'reach': result1['reach']
            })

        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'])

        return jsonify({
            "Success": True,
            "message": "Login Successful",
            "token": token,
            "role": result['role'],
        }), 200
    return jsonify({"Success": False, "message": "Something Went Wrong!"}), 401
#Registration API for both user and Serviceman

@users_blueprint.route('/register', methods=['POST'])
def register():
    action = request.form.get("action")  # For form data
    base_url = request.host_url

    username = request.form.get("username")
    password = request.form.get("password")
    mail = request.form.get("mail")
    full_name = request.form.get("full_name")
    date_created = datetime.datetime.utcnow().date()

    if action == "influencer_reg":
        niche = request.form.get("niche")
        reach = request.form.get("reach")
        category = request.form.get("category")

    if action == "sponsor_reg":
        company = request.form.get("company_name")
        industry = request.form.get("industry")

    pass_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM Users WHERE username = ?', (username,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return Response('Username already exists! Try another username.', mimetype='text/plain'), 409

    cursor.execute('SELECT COUNT(*) FROM Users WHERE mail = ?', (mail,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return Response('Email already exists! Try another email.', mimetype='text/plain'), 409

    if action == "influencer_reg":
        cursor.execute('INSERT INTO Users (username, pass_hash, role, mail, full_name, date_created) VALUES (?,?,?,?,'
                       '?,?)',
                       (username, pass_hash, "influencer", mail, full_name, date_created))

        last_id = cursor.lastrowid

        cursor.execute('INSERT INTO influencers (user_id, influencer_name, category, niche, reach) VALUES (?,?,?,?,?)',(last_id, full_name, category, niche, reach))

    elif action == "sponsor_reg":
        cursor.execute('INSERT INTO Users (username, pass_hash, role, mail, full_name, date_created'
                       ') VALUES (?,?,?,?,?,?)',
                       (username, pass_hash, "sponsor", mail, full_name, date_created))

        last_id = cursor.lastrowid

        cursor.execute('INSERT INTO sponsors (user_id, company_name, industry) VALUES (?,?,?)',
                       (last_id, company, industry))

    else:
        return Response('An Error has Occurred!.', mimetype='text/plain'), 500
    conn.commit()
    conn.close()
    return Response('Registration successful!', mimetype='text/plain'), 200


@users_blueprint.route('/get_all_users', methods=['GET'])
@token_required
def get_all_users():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT user_id, username, full_name, mail, role, date_created, flag, approval
            FROM Users
            WHERE role != 'admin'
        ''')

        users = cursor.fetchall()
        connection.close()

        users_list = []
        for user in users:
            users_list.append({
                'user_id': user[0],
                'username': user[1],
                'full_name': user[2],
                'mail': user[3],
                'role': user[4],
                'date_created': user[5],
                'flag': user[6],
                'approval': user[7]
            })

        return jsonify({'users': users_list}), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400


@users_blueprint.route('/change_approval/<int:user_id>', methods=['PUT'])
@token_required
def change_approval(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        cursor.execute('SELECT approval FROM Users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if not result:
            connection.close()
            return jsonify({'status': 'User not found'}), 404

        # Flip the approval status
        current_approval = result[0]
        new_approval = not current_approval

        # Update the approval status in the database
        cursor.execute('UPDATE Users SET approval = ? WHERE user_id = ?', (new_approval, user_id))

        connection.commit()
        connection.close()

        return jsonify({
            'status': 'User approval status updated successfully',
            'user_id': user_id,
            'new_approval_status': new_approval
        }), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400



@users_blueprint.route('/change_flag/<int:user_id>', methods=['PUT'])
@token_required
def change_flag(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        cursor.execute('SELECT flag FROM Users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if not result:
            connection.close()
            return jsonify({'status': 'User not found'}), 404

        # Flip the flag status
        current_flag = result[0]
        new_flag = not current_flag

        # Update the flag status in the database
        cursor.execute('UPDATE Users SET flag = ? WHERE user_id = ?', (new_flag, user_id))

        connection.commit()
        connection.close()

        return jsonify({
            'status': 'User flag status updated successfully',
            'user_id': user_id,
            'new_flag_status': new_flag
        }), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400



