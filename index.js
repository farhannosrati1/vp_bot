
import { Telegraf, Markup } from "telegraf";
import dotenv from "dotenv";
import axios from "axios";
import { connectDB, User } from "./db.js";
import { plans } from "./plans.js";

dotenv.config();
await connectDB(process.env.MONGO_URI);

const bot = new Telegraf(process.env.BOT_TOKEN);

async function getOrCreateUser(tgId){
  let user = await User.findOne({ tgId });
  if(!user){
    user = await User.create({ tgId });
  }
  return user;
}

async function createVPN(planKey){
  const plan = plans[planKey];

  const res = await axios.post(process.env.API_URL, {
    plan: planKey,
    gb: plan.gb,
    month: plan.month
  },{
    headers: { Authorization: `Bearer ${process.env.API_TOKEN}` }
  });

  return res.data;
}

bot.start(async (ctx)=>{
  await getOrCreateUser(ctx.from.id);

  ctx.reply("👋 خوش آمدید",
    Markup.inlineKeyboard([
      [Markup.button.callback("🛒 خرید سرویس", "buy")],
      [Markup.button.callback("💰 کیف پول", "wallet")],
      [Markup.button.callback("🎧 پشتیبانی", "support")]
    ])
  );
});

bot.action("wallet", async (ctx)=>{
  const user = await getOrCreateUser(ctx.from.id);
  ctx.reply(`💰 موجودی شما: ${user.wallet} تومان`);
});

bot.action("buy", (ctx)=>{
  ctx.editMessageText("انتخاب پلن:",
    Markup.inlineKeyboard([
      [Markup.button.callback("10GB - 100K", "p10")],
      [Markup.button.callback("20GB - 200K", "p20")],
      [Markup.button.callback("30GB - 300K", "p30")],
      [Markup.button.callback("50GB - 500K", "p50")],
      [Markup.button.callback("👑 VIP 800K", "vip")]
    ])
  );
});

for(const key of Object.keys(plans)){
  bot.action(key, async (ctx)=>{
    const user = await getOrCreateUser(ctx.from.id);
    const plan = plans[key];

    if(user.wallet < plan.price){
      return ctx.reply("❌ موجودی کافی نیست");
    }

    user.wallet -= plan.price;
    await user.save();

    const data = await createVPN(key);

    ctx.reply("✅ سرویس ساخته شد:
" + JSON.stringify(data));
  });
}

bot.action("support",(ctx)=>{
  ctx.reply("🎧 پشتیبانی: @support");
});

bot.launch();
console.log("Bot running");
