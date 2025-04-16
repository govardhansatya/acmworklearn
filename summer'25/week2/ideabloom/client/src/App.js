import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import InputBox from './components/InputBox';
import OutputCard from './components/OutputCard';

function App() {
  const { 
    loginWithRedirect, 
    logout, 
    isAuthenticated, 
    user, 
    isLoading, 
    getAccessTokenSilently 
  } = useAuth0();
  
  const [output, setOutput] = useState(null);
  const [sessionId, setSessionId] = useState(() => localStorage.getItem('session_id') || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // API URL from environment variable with fallback
  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      loginWithRedirect();
    }
  }, [isLoading, isAuthenticated, loginWithRedirect]);

  const handleSubmit = async (text, type) => {
    if (!isAuthenticated || !user || !user.sub) {
      setError("User not authenticated!");
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      // Get the access token
      const token = await getAccessTokenSilently({
        audience: process.env.REACT_APP_AUTH0_AUDIENCE,
      });
      
      const payload = {
        user_id: user.sub,
        session_id: sessionId,
        input_text: text,
        type: type,
      };

      const res = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Error generating content");
      }

      const data = await res.json();
      
      // Save session ID if it's new
      if (data.session_id && (!sessionId || sessionId !== data.session_id)) {
        localStorage.setItem("session_id", data.session_id);
        setSessionId(data.session_id);
      }

      setOutput(data.output);
    } catch (err) {
      console.error("API Error:", err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  // Function to submit feedback
  const submitFeedback = async (outputId, feedback) => {
    if (!isAuthenticated || !user) return;

    try {
      const token = await getAccessTokenSilently();
      
      const response = await fetch(`${API_URL}/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: user.sub,
          output_id: outputId,
          feedback: feedback
        })
      });

      if (!response.ok) {
        throw new Error("Failed to submit feedback");
      }
      
      return await response.json();
    } catch (err) {
      console.error("Feedback Error:", err);
      return null;
    }
  };

  // Updated OutputCard component to include feedback
  const renderOutput = () => {
    if (!output) return null;
    
    return (
      <div className="mt-6">
        <OutputCard 
          text={output} 
          onFeedback={submitFeedback} 
        />
        
        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-800 rounded">
            {error}
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading authentication...</div>;
  }

  return isAuthenticated ? (
    <div className="min-h-screen p-6 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">🎨 Creative Buddy</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm">{user.name || user.email}</span>
            <button
              onClick={() => logout({ returnTo: window.location.origin })}
              className="text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
        
        <InputBox onSubmit={handleSubmit} loading={loading} />
        {renderOutput()}
      </div>
    </div>
  ) : null;
}

export default App;