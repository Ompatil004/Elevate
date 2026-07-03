const mongoose = require('mongoose');
require('dotenv').config();

const MONGO_URI = process.env.MONGO_URI || process.env.MONGODB_URI;

async function run() {
  await mongoose.connect(MONGO_URI);
  const users = await mongoose.connection.db.collection('users').find({ latestNutritionPlan: { $ne: null } }).toArray();
  console.log('Users with nutrition plan:', users.length);
  users.forEach(u => {
    console.log(`User: ${u.email}`);
    const plan = u.latestNutritionPlan;
    if (plan && plan.weekly_plan) {
      const days = Object.keys(plan.weekly_plan);
      console.log('  Days in weekly_plan:', days);
      if (days.length > 0) {
        const firstDay = plan.weekly_plan[days[0]];
        const meals = Object.keys(firstDay);
        console.log('  Meals in first day:', meals);
        if (meals.length > 0) {
          const firstMeal = firstDay[meals[0]];
          console.log('  First meal foods sample:', firstMeal.slice(0, 1));
        }
      }
    } else {
      console.log('  No weekly_plan key in latestNutritionPlan');
      console.log('  Plan keys:', Object.keys(plan));
    }
  });
  await mongoose.disconnect();
}
run().catch(console.error);
