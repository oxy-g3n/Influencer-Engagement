from flask import Blueprint, jsonify, request
from utils import get_db_connection, token_required
import bcrypt

sponsor_blueprint = Blueprint('sponsor', __name__)


@sponsor_blueprint.route('/get_all_sponsors', methods=['GET'])
@token_required
def get_all_sponsors():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT u.user_id, u.username, u.full_name, u.mail, u.date_created, u.flag, u.approval,
                   s.company_name, s.industry
            FROM Users u
            JOIN sponsors s ON u.user_id = s.user_id
            WHERE u.role = 'sponsor'
        ''')

        sponsors = cursor.fetchall()
        connection.close()

        sponsors_list = []
        for sponsor in sponsors:
            sponsors_list.append({
                'user_id': sponsor[0],
                'username': sponsor[1],
                'full_name': sponsor[2],
                'mail': sponsor[3],
                'date_created': sponsor[4],
                'flag': sponsor[5],
                'approval': sponsor[6],
                'company_name': sponsor[7],
                'industry': sponsor[8]
            })

        return jsonify({'sponsors': sponsors_list}), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400


@sponsor_blueprint.route('/update_profile/<int:user_id>', methods=['PUT'])
@token_required
def update_sponsor_profile(user_id):
    try:
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the user exists and is a sponsor
        cursor.execute('SELECT role FROM Users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if not result or result[0] != 'sponsor':
            connection.close()
            return jsonify({'status': 'User not found or not a sponsor'}), 404

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

        # Update sponsors table
        update_sponsor_query = '''
        UPDATE sponsors 
        SET company_name = ?, industry = ?
        WHERE user_id = ?
        '''
        cursor.execute(update_sponsor_query, (data['company_name'], data['industry'], user_id))

        # Update campaigns table with new company name and industry
        update_campaigns_query = '''
        UPDATE Campaigns 
        SET company_name = ?, industry = ?
        WHERE sponsor_id = ?
        '''
        cursor.execute(update_campaigns_query, (data['company_name'], data['industry'], user_id))

        connection.commit()
        connection.close()

        return jsonify({
            'status': 'Sponsor profile updated successfully',
            'user_id': user_id
        }), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400


@sponsor_blueprint.route('/get_sponsor/<int:id>', methods=['GET'])
@token_required
def get_sponsor(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT u.user_id, u.username, u.full_name, u.mail, u.date_created, u.flag, u.approval,
                   s.company_name, s.industry
            FROM Users u
            JOIN sponsors s ON u.user_id = s.user_id
            WHERE u.role = 'sponsor' AND u.user_id = ?
        ''', (id,))

        sponsor = cursor.fetchone()
        connection.close()

        if not sponsor:
            return jsonify({'status': 'error', 'message': 'Sponsor not found'}), 404

        sponsor_data = {
            'user_id': sponsor[0],
            'username': sponsor[1],
            'full_name': sponsor[2],
            'mail': sponsor[3],
            'date_created': sponsor[4],
            'flag': sponsor[5],
            'approval': sponsor[6],
            'company_name': sponsor[7],
            'industry': sponsor[8]
        }

        return jsonify({'sponsor': sponsor_data}), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400
