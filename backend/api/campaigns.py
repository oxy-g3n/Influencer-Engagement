from flask import Blueprint, request, Response, jsonify
import datetime
from utils import get_db_connection, token_required

campaigns_blueprint = Blueprint('campaigns', __name__)


@campaigns_blueprint.route('/make_campaign', methods=['POST'])
@token_required
def make_campaign():
    try:
        data_token = request.token_data
        user_id = data_token['user_id']

        connection = get_db_connection()
        cursor = connection.cursor()

        sponsor_id = user_id
        campaign_name = request.json['campaign_name']
        campaign_description = request.json['campaign_description']
        campaign_goals = request.json['campaign_goals']
        campaign_start_date = datetime.datetime.utcnow().date()
        campaign_end_date = request.json['campaign_end_date']
        budget = request.json['budget']
        visibility = request.json['visibility']
        niche = request.json['niche']
        company_name = request.json['company_name']
        industry = request.json['industry']

        # Validate campaign_end_date
        try:
            campaign_end_date = datetime.datetime.strptime(campaign_end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'status': 'Invalid date format for campaign_end_date. Use YYYY-MM-DD'}), 400

        # Check if campaign already exists
        cursor.execute('SELECT COUNT(*) FROM Campaigns WHERE campaign_name = ?', (campaign_name,))
        if cursor.fetchone()[0] > 0:
            connection.close()
            return jsonify({'status': 'Campaign already exists'}), 400

        # Insert new campaign
        cursor.execute('''
            INSERT INTO Campaigns (sponsor_id, campaign_name, campaign_description, campaign_goals, 
            campaign_start_date, campaign_end_date, budget, visibility, niche, company_name, industry) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', (sponsor_id, campaign_name, campaign_description, campaign_goals,
              campaign_start_date, campaign_end_date, budget, visibility, niche, company_name, industry))

        connection.commit()
        connection.close()
        return jsonify({'status': 'Campaign created! Please Reload the Page.'}), 201

    except KeyError as e:
        return jsonify({'status': 'Missing required field', 'field': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400


@campaigns_blueprint.route('/edit_campaign/<int:campaign_id>', methods=['PUT'])
@token_required
def edit_campaign(campaign_id):
    try:
        data_token = request.token_data
        user_id = data_token['user_id']

        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the campaign exists and belongs to the user
        cursor.execute('SELECT sponsor_id FROM Campaigns WHERE campaign_id = ?', (campaign_id,))
        result = cursor.fetchone()
        if not result:
            connection.close()
            return jsonify({'status': 'Campaign not found'}), 404
        if result[0] != user_id:
            connection.close()
            return jsonify({'status': 'Unauthorized to edit this campaign'}), 403

        # Get the fields to update from the request
        campaign_name = request.json['campaign_name']
        campaign_description = request.json['campaign_description']
        campaign_goals = request.json['campaign_goals']
        campaign_end_date = request.json['campaign_end_date']
        budget = request.json['budget']
        niche = request.json['niche']

        # Validate campaign_end_date
        try:
            campaign_end_date = datetime.datetime.strptime(campaign_end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'status': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Update the campaign
        cursor.execute('''
            UPDATE Campaigns 
            SET campaign_name = ?, campaign_description = ?, campaign_goals = ?, campaign_end_date = ?, budget = ?, niche = ?
            WHERE campaign_id = ?
        ''', (campaign_name, campaign_description, campaign_goals, campaign_end_date, budget, niche, campaign_id))

        connection.commit()
        connection.close()

        return jsonify({'status': 'Campaign updated successfully! Please Reload the Page'}), 200

    except KeyError as e:
        return jsonify({'status': 'Missing required field', 'field': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400


@campaigns_blueprint.route('/edit_visibility/<int:campaign_id>', methods=['PUT'])
@token_required
def edit_visibility(campaign_id):
    try:
        data_token = request.token_data
        user_id = data_token['user_id']

        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the campaign exists and belongs to the user
        cursor.execute('SELECT sponsor_id, visibility FROM Campaigns WHERE campaign_id = ?', (campaign_id,))
        result = cursor.fetchone()
        if not result:
            connection.close()
            return jsonify({'status': 'Campaign not found'}), 404
        if result[0] != user_id:
            connection.close()
            return jsonify({'status': 'Unauthorized to edit this campaign'}), 403

        # Flip the visibility
        current_visibility = result[1]
        new_visibility = not current_visibility

        # Update the visibility in the database
        cursor.execute('UPDATE Campaigns SET visibility = ? WHERE campaign_id = ?', (new_visibility, campaign_id))

        connection.commit()
        connection.close()

        return jsonify({
            'status': 'Campaign visibility updated successfully',
            'new_visibility': new_visibility
        }), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400



@campaigns_blueprint.route('/get_all_campaigns', methods=['GET'])
@token_required
def get_all_campaigns():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT campaign_id, sponsor_id, campaign_name, campaign_description, 
                   campaign_goals, campaign_start_date, campaign_end_date, budget, visibility, niche, flag, company_name, industry
            FROM Campaigns
        ''')

        campaigns = cursor.fetchall()
        connection.close()

        campaigns_list = []
        for campaign in campaigns:
            campaigns_list.append({
                'campaign_id': campaign[0],
                'sponsor_id': campaign[1],
                'campaign_name': campaign[2],
                'campaign_description': campaign[3],
                'campaign_goals': campaign[4],
                'campaign_start_date': campaign[5],
                'campaign_end_date': campaign[6],
                'budget': campaign[7],
                'visibility': campaign[8],
                'niche': campaign[9],
                'flag': campaign[10],
                'company_name': campaign[11],
                'industry': campaign[12]
            })

        return jsonify({'campaigns': campaigns_list}), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400

@campaigns_blueprint.route('/get_campaigns/<int:id>', methods=['GET'])
@token_required
def get_campaigns(id):
    try:
        action = request.args.get('action')

        if action not in ['sponsor_id', 'campaign_id']:
            return jsonify({'status': 'Invalid action. Use "sponsor_id" or "campaign_id"'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        if action == 'sponsor_id':
            cursor.execute('''
                SELECT campaign_id, sponsor_id, campaign_name, campaign_description, 
                       campaign_goals, campaign_start_date, campaign_end_date, budget, visibility, niche, company_name, industry
                FROM Campaigns
                WHERE sponsor_id = ?
            ''', (id,))
        else:  # action == 'campaign_id'
            cursor.execute('''
                SELECT campaign_id, sponsor_id, campaign_name, campaign_description, 
                       campaign_goals, campaign_start_date, campaign_end_date, budget, visibility, niche, company_name, industry
                FROM Campaigns
                WHERE campaign_id = ?
            ''', (id,))

        campaigns = cursor.fetchall()
        connection.close()

        campaigns_list = []
        for campaign in campaigns:
            campaigns_list.append({
                'campaign_id': campaign[0],
                'sponsor_id': campaign[1],
                'campaign_name': campaign[2],
                'campaign_description': campaign[3],
                'campaign_goals': campaign[4],
                'campaign_start_date': campaign[5],
                'campaign_end_date': campaign[6],
                'budget': campaign[7],
                'visibility': campaign[8],
                'niche': campaign[9],
                'company_name': campaign[10],
                'industry': campaign[11]
            })

        return jsonify({'campaigns': campaigns_list}), 200

    except KeyError:
        return jsonify({'status': 'Missing required field: action'}), 400
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400



# Assuming this is added to the existing campaigns_blueprint

@campaigns_blueprint.route('/delete_campaign/<int:campaign_id>', methods=['DELETE'])
@token_required
def delete_campaign(campaign_id):
    try:
        data_token = request.token_data
        user_id = data_token['user_id']

        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the campaign exists and belongs to the user
        cursor.execute('SELECT sponsor_id FROM Campaigns WHERE campaign_id = ?', (campaign_id,))
        result = cursor.fetchone()
        if not result:
            connection.close()
            return jsonify({'status': 'Campaign not found'}), 404
        if result[0] != user_id:
            connection.close()
            return jsonify({'status': 'Unauthorized to delete this campaign'}), 403

        # Delete the campaign
        cursor.execute('DELETE FROM Campaigns WHERE campaign_id = ?', (campaign_id,))

        connection.commit()
        connection.close()

        return jsonify({'status': 'Campaign deleted successfully'}), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400



@campaigns_blueprint.route('/change_campaign_flag/<int:campaign_id>', methods=['PUT'])
@token_required
def change_flag(campaign_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        cursor.execute('SELECT flag FROM Campaigns WHERE campaign_id = ?', (campaign_id,))
        result = cursor.fetchone()
        if not result:
            connection.close()
            return jsonify({'status': 'Campaign not found'}), 404

        # Flip the flag status
        current_flag = result[0]
        new_flag = not current_flag

        # Update the flag status in the database
        cursor.execute('UPDATE Campaigns SET flag = ? WHERE campaign_id = ?', (new_flag, campaign_id))

        connection.commit()
        connection.close()

        return jsonify({
            'status': 'User flag status updated successfully',
            'campaign_id': campaign_id,
            'new_flag_status': new_flag
        }), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400
