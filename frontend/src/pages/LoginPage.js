import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { Eye, EyeOff, LogIn } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const LoginPage = ({ setToken }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
        email,
        password
      });
      
      setToken(response.data.token);
      toast.success("Login successful!");
      navigate("/quiz");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center hero-gradient px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl md:text-4xl text-[#0f172a] mb-2">Welcome Back</h1>
            <p className="text-[#475569]">Login to check your eligibility</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label htmlFor="email" className="text-sm font-medium text-slate-700 mb-2 block">
                Email Address
              </label>
              <input
                id="email"
                data-testid="login-email-input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full h-12 rounded-lg border-2 border-slate-300 focus:ring-2 focus:ring-[#1e3a8a] focus:border-transparent bg-white text-lg px-4"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="text-sm font-medium text-slate-700 mb-2 block">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  data-testid="login-password-input"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full h-12 rounded-lg border-2 border-slate-300 focus:ring-2 focus:ring-[#1e3a8a] focus:border-transparent bg-white text-lg px-4 pr-12"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <button
              data-testid="login-submit-btn"
              type="submit"
              disabled={loading}
              className="w-full bg-[#ea580c] hover:bg-[#c2410c] text-white font-medium px-8 py-3 rounded-full transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <span className="loading-pulse">Logging in...</span>
              ) : (
                <>
                  <LogIn size={20} />
                  Login
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-[#475569]">
              Don't have an account?{" "}
              <Link to="/signup" className="text-[#1e3a8a] hover:text-[#172554] font-medium">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
