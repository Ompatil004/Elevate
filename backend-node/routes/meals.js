const express = require('express');
const auth = require('../middleware/auth');
const Meal = require('../models/Meal');

const router = express.Router();

// @route    POST api/meals
// @desc     Create a new meal
// @access   Private
router.post('/', auth, async (req, res) => {
  try {
    const { name, description, mealType, ingredients, prepTime, difficulty, dietaryRestrictions, recipe, nutritionGoals } = req.body;

    // Calculate total calories and macros
    const totalCalories = ingredients.reduce((acc, ingredient) => acc + ingredient.calories, 0);
    const protein = ingredients.reduce((acc, ingredient) => acc + (ingredient.protein || 0), 0);
    const carbs = ingredients.reduce((acc, ingredient) => acc + (ingredient.carbs || 0), 0);
    const fat = ingredients.reduce((acc, ingredient) => acc + (ingredient.fat || 0), 0);

    const newMeal = new Meal({
      userId: req.user.id,
      name,
      description,
      mealType,
      ingredients,
      totalCalories,
      protein,
      carbs,
      fat,
      prepTime,
      difficulty,
      dietaryRestrictions,
      recipe,
      nutritionGoals
    });

    const meal = await newMeal.save();
    res.json(meal);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    GET api/meals
// @desc     Get all meals for a user
// @access   Private
router.get('/', auth, async (req, res) => {
  try {
    const meals = await Meal.find({ userId: req.user.id }).sort({ createdAt: -1 });
    res.json(meals);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    GET api/meals/public
// @desc     Get all public meals
// @access   Public
router.get('/public', async (req, res) => {
  try {
    const meals = await Meal.find({ isPublic: true }).sort({ createdAt: -1 });
    res.json(meals);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    GET api/meals/:id
// @desc     Get a specific meal
// @access   Private
router.get('/:id', auth, async (req, res) => {
  try {
    const meal = await Meal.findById(req.params.id);

    if (!meal) {
      return res.status(404).json({ msg: 'Meal not found' });
    }

    res.json(meal);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    PUT api/meals/:id
// @desc     Update a meal
// @access   Private
router.put('/:id', auth, async (req, res) => {
  try {
    let meal = await Meal.findById(req.params.id);

    if (!meal) {
      return res.status(404).json({ msg: 'Meal not found' });
    }

    // Check user
    if (meal.userId.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    const { name, description, mealType, ingredients, prepTime, difficulty, dietaryRestrictions, recipe, nutritionGoals, isPublic } = req.body;

    // Calculate total calories and macros
    const totalCalories = ingredients ? ingredients.reduce((acc, ingredient) => acc + ingredient.calories, 0) : meal.totalCalories;
    const protein = ingredients ? ingredients.reduce((acc, ingredient) => acc + (ingredient.protein || 0), 0) : meal.protein;
    const carbs = ingredients ? ingredients.reduce((acc, ingredient) => acc + (ingredient.carbs || 0), 0) : meal.carbs;
    const fat = ingredients ? ingredients.reduce((acc, ingredient) => acc + (ingredient.fat || 0), 0) : meal.fat;

    const mealFields = {};
    if (name) mealFields.name = name;
    if (description) mealFields.description = description;
    if (mealType) mealFields.mealType = mealType;
    if (ingredients) mealFields.ingredients = ingredients;
    if (totalCalories) mealFields.totalCalories = totalCalories;
    if (protein) mealFields.protein = protein;
    if (carbs) mealFields.carbs = carbs;
    if (fat) mealFields.fat = fat;
    if (prepTime) mealFields.prepTime = prepTime;
    if (difficulty) mealFields.difficulty = difficulty;
    if (dietaryRestrictions) mealFields.dietaryRestrictions = dietaryRestrictions;
    if (recipe) mealFields.recipe = recipe;
    if (nutritionGoals) mealFields.nutritionGoals = nutritionGoals;
    if (typeof isPublic !== 'undefined') mealFields.isPublic = isPublic;

    meal = await Meal.findByIdAndUpdate(
      req.params.id,
      { $set: mealFields },
      { new: true }
    );

    res.json(meal);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    DELETE api/meals/:id
// @desc     Delete a meal
// @access   Private
router.delete('/:id', auth, async (req, res) => {
  try {
    const meal = await Meal.findById(req.params.id);

    if (!meal) {
      return res.status(404).json({ msg: 'Meal not found' });
    }

    // Check user
    if (meal.userId.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    await Meal.findByIdAndRemove(req.params.id);

    res.json({ msg: 'Meal removed' });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

module.exports = router;