const express = require('express');
const auth = require('../middleware/auth');
const {
  getAllExercises,
  getExerciseById,
  createExercise,
  updateExercise,
  deleteExercise
} = require('../controllers/ExerciseController');

const router = express.Router();

// @route    GET api/exercises/test
// @desc     Test exercises route
// @access   Public
router.get('/test', (req, res) => {
  res.json({ msg: 'Exercises route is working!' });
});

// @route    GET api/exercises
// @desc     Get all exercises
// @access   Private
router.get('/', auth, getAllExercises);

// @route    GET api/exercises/:id
// @desc     Get exercise by ID
// @access   Private
router.get('/:id', auth, getExerciseById);

// @route    POST api/exercises
// @desc     Add new exercise
// @access   Private
router.post('/', auth, createExercise);

// @route    PUT api/exercises/:id
// @desc     Update exercise
// @access   Private
router.put('/:id', auth, updateExercise);

// @route    DELETE api/exercises/:id
// @desc     Delete exercise
// @access   Private
router.delete('/:id', auth, deleteExercise);

module.exports = router;