
import mongoose from "mongoose";

export async function connectDB(uri){
  await mongoose.connect(uri);
  console.log("DB connected");
}

export const userSchema = new mongoose.Schema({
  tgId: String,
  wallet: { type: Number, default: 0 },
  createdAt: { type: Date, default: Date.now }
});

export const User = mongoose.model("User", userSchema);
