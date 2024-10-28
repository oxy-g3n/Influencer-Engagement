from flask import Blueprint, request, jsonify
from utils import get_db_connection, token_required

ads_blueprint = Blueprint('ads', __name__)


@ads_blueprint.route('/make_ad_request', methods=['POST'])
@token_required
def make_request():
    try:
        data_token = request.token_data
        user_id = data_token['user_id']

        role = data_token['role']
        if role != 'sponsor':
            return jsonify({'error': 'You are not authorized to create this ad request'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        influencer_id = request.json['influencer_id']
        campaign_id = request.json['campaign_id']
        # Check if the campaign exists and belongs to the user
        cursor.execute('SELECT COUNT(*) FROM Users WHERE user_id = ?', (influencer_id,))
        result = cursor.fetchone()
        if result[0] == 0:
            connection.close()
            return jsonify({'status': 'Influencer with that ID does not exist'}), 404

        cursor.execute('SELECT COUNT(*) FROM Campaigns WHERE campaign_id = ?', (campaign_id,))
        result1 = cursor.fetchone()
        if result1[0] == 0:
            connection.close()
            return jsonify({'status': 'Campaign with that ID does not exist'}), 404

        sponsor_id = user_id
        requirements = request.json['requirements']
        payout = request.json['payout']
        status = "open"

        cursor.execute('''
        INSERT INTO Ad_Requests (campaign_id, sponsor_id, influencer_id, requirements, payout, status) 
        VALUES (?,?,?,?,?,?)''', (campaign_id, sponsor_id, influencer_id, requirements, payout, status))

        connection.commit()
        connection.close()

        return jsonify({'status': 'Successfully created Request'}), 201

    except KeyError as e:
        return jsonify({'status': 'Missing required field', 'field': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400


@ads_blueprint.route('/make_ad_request/<int:campaign_id>', methods=['POST'])
@token_required
def make_InfluencerAdRequest(campaign_id):
    try:
        data_token = request.token_data
        user_id = data_token['user_id']

        role = data_token['role']
        if role != 'influencer':
            return jsonify({'error': 'You are not authorized to use this request'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        influencer_id = user_id

        # Check if the campaign exists and belongs to the user
        cursor.execute('SELECT COUNT(*) FROM Campaigns WHERE campaign_id = ?', (campaign_id,))
        result = cursor.fetchone()
        if result[0] == 0:
            connection.close()
            return jsonify({'status': 'Campaign with that ID does not exist'}), 404

        # Check if the campaign exists and belongs to the user
        cursor.execute('SELECT COUNT(*) FROM Ad_Requests WHERE campaign_id = ? AND influencer_id = ? AND (status = ? '
                       'OR status = ? OR status = ?)', (campaign_id,influencer_id, "influencer_generated",
                                                        "accepted", "modified"))
        result1 = cursor.fetchone()
        if result1[0] != 0:
            connection.close()
            return jsonify({'status': 'A previous request is pending!'}), 400

        sponsor_id = request.json['sponsor_id']
        payout = request.json['payout']
        status = "influencer_generated"

        cursor.execute('''
        INSERT INTO Ad_Requests (campaign_id, sponsor_id, influencer_id, payout, status) 
        VALUES (?,?,?,?,?)''', (campaign_id, sponsor_id, influencer_id, payout, status))

        connection.commit()
        connection.close()

        return jsonify({'status': 'Successfully created Request'}), 201

    except KeyError as e:
        return jsonify({'status': 'Missing required field', 'field': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400


@ads_blueprint.route('/edit_ad_request/<int:adRequest_id>', methods=['PUT'])
@token_required
def edit_request(adRequest_id):
    try:
        data_token = request.token_data
        user_id = data_token['user_id']

        role = data_token['role']

        connection = get_db_connection()
        cursor = connection.cursor()

        if role == "sponsor":
            influencer_id = request.json['influencer_id']

            cursor.execute('SELECT COUNT(*) FROM Users WHERE user_id = ? AND role = ?', (influencer_id, "influencer",))
            result = cursor.fetchone()
            if result[0] == 0:
                connection.close()
                return jsonify({'status': 'Influencer with that ID does not exist'}), 404

            requirements = request.json['requirements']
            payout = request.json['payout']

            cursor.execute('''
            UPDATE Ad_Requests
            SET influencer_id=?, requirements=?, payout=? 
            WHERE adRequest_id=?''', (influencer_id, requirements, payout, adRequest_id))
            connection.commit()
            connection.close()

            return jsonify({'status': 'Successfully modified Request'}), 200

        if role == "influencer":
            status = "modified"
            new_payout = request.json['new_payout']
            cursor.execute('''
                        UPDATE Ad_Requests
                        SET new_payout=?, status=? 
                        WHERE adRequest_id=?''', (new_payout, status, adRequest_id))

            connection.commit()
            connection.close()

            return jsonify({'status': 'Successfully requested new payout'}), 200

    except KeyError as e:
        return jsonify({'status': 'Missing required field', 'field': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400


@ads_blueprint.route('/edit_ad_status/<int:adRequest_id>', methods=['PUT'])
@token_required
def edit_status(adRequest_id):
    try:
        data_token = request.token_data
        user_id = data_token['user_id']

        connection = get_db_connection()
        cursor = connection.cursor()

        current_status = request.json['current_status']
        new_status = request.json['new_status']

        if (new_status == "completed") or (new_status == "modification_rejected") or (new_status == "rejected") or (new_status == "withdrawn") or (new_status == "completed"):
            cursor.execute('''UPDATE Ad_Requests SET status=? WHERE adRequest_id=?''', (new_status, adRequest_id))

            connection.commit()
            connection.close()
            return jsonify({'status': 'Successfully updated status'}), 200

        if new_status == "modification_accepted":
            cursor.execute('SELECT new_payout FROM Ad_Requests WHERE adRequest_id=?', (adRequest_id,))
            new_payout = cursor.fetchone()
            cursor.execute('''
                UPDATE Ad_Requests
                SET status=?, payout=?
                WHERE adRequest_id=?''', (new_status, new_payout[0], adRequest_id))
            connection.commit()
            connection.close()
            return jsonify({'status': 'Successfully accepted modification'}), 200

        if new_status == "accepted" and current_status == "influencer_generated":
            requirements = request.json['requirements']
            cursor.execute('''
                UPDATE Ad_Requests
                SET status=?, requirements=?
                WHERE adRequest_id=?''', (new_status, requirements, adRequest_id))
            connection.commit()
            connection.close()
            return jsonify({'status': 'Successfully accepted request'}), 200

        elif new_status == "accepted" and current_status != "influencer_generated":
            cursor.execute('''
                UPDATE Ad_Requests
                SET status=?
                WHERE adRequest_id=?''', (new_status, adRequest_id))
            connection.commit()
            connection.close()
            return jsonify({'status': 'Successfully accepted request'}), 200
    except KeyError as e:
        return jsonify({'status': 'Missing required field', 'field': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400

@ads_blueprint.route('/get_ads/<int:id>', methods=['GET'])
@token_required
def get_ads(id):
    try:
        action = request.args.get('action')

        if action not in ['sponsor_id', 'campaign_id', 'influencer_id']:
            return jsonify({'status': 'Invalid action. Use "sponsor_id", "campaign_id" or "influencer_id"'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        if action == 'sponsor_id':
            cursor.execute('''
                SELECT adRequest_id, campaign_id, sponsor_id, influencer_id, requirements, payout, status, new_payout
                FROM Ad_Requests
                WHERE sponsor_id = ?
            ''', (id,))
        elif action == 'campaign_id':
            cursor.execute('''
                SELECT adRequest_id, campaign_id, sponsor_id, influencer_id, requirements, payout, status, new_payout
                FROM Ad_Requests
                WHERE campaign_id = ?
            ''', (id,))
        else:
            cursor.execute('''
                 SELECT adRequest_id, campaign_id, sponsor_id, influencer_id, requirements, payout, status, new_payout
                 FROM Ad_Requests
                 WHERE influencer_id = ?
                 ''', (id,))
        ads = cursor.fetchall()
        connection.close()
        ads_list = []
        for ad in ads:
            ads_list.append({
                'adRequest_id': ad[0],
                'campaign_id': ad[1],
                'sponsor_id': ad[2],
                'influencer_id': ad[3],
                'requirements': ad[4],
                'payout': ad[5],
                'status': ad[6],
                'new_payout': ad[7]
            })

        return jsonify({'ads': ads_list}), 200

    except KeyError:
        return jsonify({'status': 'Missing required field: action'}), 400
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400



@ads_blueprint.route('/get_all_ads', methods=['GET'])
@token_required
def get_all_campaigns():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT adRequest_id, campaign_id, sponsor_id, influencer_id, requirements, payout, status, new_payout
            FROM Ad_Requests
        ''')

        ads = cursor.fetchall()
        connection.close()

        ads_list = []
        for ad in ads:
            ads_list.append({
                'adRequest_id': ad[0],
                'campaign_id': ad[1],
                'sponsor_id': ad[2],
                'influencer_id': ad[3],
                'requirements': ad[4],
                'payout': ad[5],
                'status': ad[6],
                'new_payout': ad[7]
            })

        return jsonify({'ads': ads_list}), 200

    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 400
