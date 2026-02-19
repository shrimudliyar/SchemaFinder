import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { ArrowRight, ArrowLeft } from "lucide-react";
import { Progress } from "@/components/ui/progress";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
];

const QuizPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    age: "",
    gender: "",
    state: "",
    area: "",
    income: "",
    occupation: "",
    education: "",
    category: "",
    has_land: "",
    is_disabled: ""
  });

  const questions = [
    {
      id: "age",
      question: "What is your age?",
      type: "number",
      placeholder: "Enter your age"
    },
    {
      id: "gender",
      question: "What is your gender?",
      type: "radio",
      options: ["Male", "Female", "Other"]
    },
    {
      id: "state",
      question: "Which state do you belong to?",
      type: "select",
      options: INDIAN_STATES
    },
    {
      id: "area",
      question: "Do you live in Urban or Rural area?",
      type: "radio",
      options: ["Urban", "Rural"]
    },
    {
      id: "income",
      question: "What is your annual family income?",
      type: "radio",
      options: ["Below ₹1,00,000", "₹1,00,000 – ₹3,00,000", "₹3,00,000 – ₹8,00,000", "Above ₹8,00,000"]
    },
    {
      id: "occupation",
      question: "What is your current occupation?",
      type: "radio",
      options: ["Student", "Farmer", "Self-employed", "Salaried", "Unemployed", "Senior Citizen"]
    },
    {
      id: "education",
      question: "What is your highest education level?",
      type: "radio",
      options: ["School", "Diploma", "Undergraduate", "Postgraduate", "Not Applicable"]
    },
    {
      id: "category",
      question: "Do you belong to any of these categories?",
      type: "radio",
      options: ["SC", "ST", "OBC", "General", "Prefer not to say"]
    },
    {
      id: "has_land",
      question: "Do you have agricultural land?",
      type: "radio",
      options: ["Yes", "No"]
    },
    {
      id: "is_disabled",
      question: "Are you a person with disability (Divyang)?",
      type: "radio",
      options: ["Yes", "No"]
    }
  ];

  const progress = ((currentStep + 1) / questions.length) * 100;
  const currentQuestion = questions[currentStep];

  const handleNext = () => {
    if (!formData[currentQuestion.id]) {
      toast.error("Please answer this question");
      return;
    }
    
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const payload = {
        ...formData,
        age: parseInt(formData.age)
      };
      
      const response = await axios.post(
        `${BACKEND_URL}/api/quiz/submit`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      navigate('/results', { state: response.data });
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to submit quiz");
    } finally {
      setLoading(false);
    }
  };

  const renderQuestion = () => {
    const q = currentQuestion;
    
    if (q.type === "number") {
      return (
        <input
          data-testid={`quiz-${q.id}-input`}
          type="number"
          value={formData[q.id]}
          onChange={(e) => setFormData({ ...formData, [q.id]: e.target.value })}
          placeholder={q.placeholder}
          min="1"
          max="120"
          className="w-full h-14 rounded-lg border-2 border-slate-300 focus:ring-2 focus:ring-[#1e3a8a] focus:border-transparent bg-white text-xl px-4"
        />
      );
    }
    
    if (q.type === "select") {
      return (
        <select
          data-testid={`quiz-${q.id}-select`}
          value={formData[q.id]}
          onChange={(e) => setFormData({ ...formData, [q.id]: e.target.value })}
          className="w-full h-14 rounded-lg border-2 border-slate-300 focus:ring-2 focus:ring-[#1e3a8a] focus:border-transparent bg-white text-lg px-4"
        >
          <option value="">Select your state</option>
          {q.options.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      );
    }
    
    if (q.type === "radio") {
      return (
        <div className="space-y-3">
          {q.options.map((option) => (
            <label
              key={option}
              data-testid={`quiz-${q.id}-option-${option.toLowerCase().replace(/\s+/g, '-')}`}
              className={`flex items-center justify-between p-6 border-2 rounded-xl cursor-pointer transition-all hover:border-[#1e3a8a] hover:bg-blue-50 ${
                formData[q.id] === option
                  ? 'border-[#1e3a8a] bg-blue-50'
                  : 'border-slate-200 bg-white'
              }`}
            >
              <span className="text-lg text-[#0f172a]">{option}</span>
              <input
                type="radio"
                name={q.id}
                value={option}
                checked={formData[q.id] === option}
                onChange={(e) => setFormData({ ...formData, [q.id]: e.target.value })}
                className="w-5 h-5 text-[#1e3a8a] focus:ring-[#1e3a8a]"
              />
            </label>
          ))}
        </div>
      );
    }
  };

  return (
    <div className="min-h-screen hero-gradient py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8 md:p-12">
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <span className="text-sm font-medium text-[#475569]">
                Question {currentStep + 1} of {questions.length}
              </span>
              <span className="text-sm font-medium text-[#1e3a8a]">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" data-testid="quiz-progress" />
          </div>

          <div className="quiz-step" key={currentStep}>
            <h2 className="text-2xl md:text-3xl text-[#0f172a] mb-8">
              {currentQuestion.question}
            </h2>
            {renderQuestion()}
          </div>

          <div className="flex gap-4 mt-8">
            {currentStep > 0 && (
              <button
                data-testid="quiz-back-btn"
                onClick={handleBack}
                className="flex-1 bg-white text-[#1e3a8a] border-2 border-[#1e3a8a] hover:bg-blue-50 font-medium px-8 py-3 rounded-full transition-all flex items-center justify-center gap-2"
              >
                <ArrowLeft size={20} />
                Back
              </button>
            )}
            <button
              data-testid="quiz-next-btn"
              onClick={handleNext}
              disabled={loading}
              className="flex-1 bg-[#ea580c] hover:bg-[#c2410c] text-white font-medium px-8 py-3 rounded-full transition-all shadow-lg hover:shadow-xl disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <span className="loading-pulse">Checking eligibility...</span>
              ) : (
                <>
                  {currentStep === questions.length - 1 ? 'Submit' : 'Next'}
                  <ArrowRight size={20} />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizPage;
