import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from "@google/generative-ai";
// import dotenv from "dotenv";

// dotenv.config();

  const apiKey = "AIzaSyAuBxYK-cy5hgQCCwfzG5InjQ7oRf4oFSA";
  const genAI = new GoogleGenerativeAI(apiKey);
  
  const model = genAI.getGenerativeModel({
    model: "gemini-1.5-flash",
  });
  
  const generationConfig = {
    temperature: 1,
    topP: 0.95,
    topK: 40,
    maxOutputTokens: 8192,
    responseMimeType: "text/plain",
  };
  
 //model to make a call
    export const chatSession = model.startChat({
      generationConfig,
      history: [
      ],
    });
  
   
  
  
  