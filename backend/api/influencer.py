from flask import Blueprint, jsonify, request
from utils import get_db_connection, token_required
import bcrypt

influencer_blueprint = Blueprint('influencer', __name__)


@influencer_blueprint.route('/get_all_influencers', methods=['GET'])
@token_required
def get_all_influencers():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT u.user_id, u.username, u.full_name, u.mail, u.date_created, u.flag, u.approval,
                   i.influencer_name, i.category, i.niche, i.reach
            FROM Users u
            JOIN influencers i ON u.user_id = i.user_id
            WHERE u.role = 'influencer'
        ''')

        influencers = cursor.fetchall()
        connection.close()

        influencers_list = []
        for influencer in influencers:
            influencers_list.append({
                'user_id': influencer[0],
                'username': influencer[1],
                'full_name': influencer[2],
                'mail': influencer[3],
                'date_created': influencer[4],
                'flag': influencer[5],
                'approval': influencer[6],
                'influencer_name': influencer[7],
                'category': influencer[8],
                'niche': influencer[9],
                'reach': influencer[10]
            })

        return jsonify({'influencers': influencers_list}), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400


@influencer_blueprint.route('/update_profile/<int:user_id>', methods=['PUT'])
@token_required
def update_influencer_profile(user_id):
    try:
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the user exists and is an influencer
        cursor.execute('SELECT role FROM Users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if not result or result[0] != 'influencer':
            connection.close()
            return jsonify({'status': 'User not found or not an influencer'}), 404

        # Update Users table
        update_user_query = '''
        UPDATE Users 
        SET full_name = ?, mail = ?
        WHERE user_id = ?
        '''
        cursor.execute(update_user_query, (data['full_name'], data['mail'], user_id))

        # Update password if provided
        if 'password' in data:
            pass_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('UPDATE Users SET pass_hash = ? WHERE user_id = ?', (pass_hash, user_id))

        # Update influencers table
        update_influencer_query = '''
        UPDATE influencers 
        SET category = ?, niche = ?, reach = ?
        WHERE user_id = ?
        '''
        cursor.execute(update_influencer_query, (data['category'], data['niche'], data['reach'], user_id))

        connection.commit()
        connection.close()

        return jsonify({
            'status': 'Influencer profile updated successfully',
            'user_id': user_id
        }), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400

@influencer_blueprint.route('/get_influencer/<int:user_id>', methods=['GET'])
@token_required
def get_influencer(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT u.user_id, u.username, u.full_name, u.mail, u.date_created, u.flag, u.approval,
                   i.influencer_name, i.category, i.niche, i.reach
            FROM Users u
            JOIN influencers i ON u.user_id = i.user_id
            WHERE u.role = 'influencer' AND u.user_id = ?
        ''', (user_id,))

        influencer = cursor.fetchone()
        connection.close()

        if not influencer:
            return jsonify({'status': 'Not found', 'message': 'Influencer not found'}), 404

        influencer_data = {
            'user_id': influencer[0],
            'username': influencer[1],
            'full_name': influencer[2],
            'mail': influencer[3],
            'date_created': influencer[4],
            'flag': influencer[5],
            'approval': influencer[6],
            'influencer_name': influencer[7],
            'category': influencer[8],
            'niche': influencer[9],
            'reach': influencer[10]
        }

        return jsonify({'influencer': influencer_data}), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400