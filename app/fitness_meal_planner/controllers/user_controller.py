"""
User Controller for managing user profiles and preferences
"""

from flask import jsonify
import json
import os
from models.user_model import UserModel


class UserController:
    def __init__(self):
        self.user_model = UserModel()

    def create_user(self, user_data):
        """Create a new user profile"""
        try:
            user_id = self.user_model.create_user(user_data)
            return jsonify({
                'success': True,
                'user_id': user_id,
                'message': 'User profile created successfully'
            }), 201
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

    def get_user(self, user_id):
        """Get user profile by ID"""
        try:
            user = self.user_model.get_user(user_id)
            if user:
                return jsonify({
                    'success': True,
                    'user': user
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def update_user(self, user_id, user_data):
        """Update user profile"""
        try:
            success = self.user_model.update_user(user_id, user_data)
            if success:
                return jsonify({
                    'success': True,
                    'message': 'User profile updated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500