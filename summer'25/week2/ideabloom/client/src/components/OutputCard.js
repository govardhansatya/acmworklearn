import React, { useState } from 'react';

function OutputCard({ text, outputId, onFeedback }) {
  const [feedback, setFeedback] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const handleSubmitFeedback = () => {
    if (feedback.trim() && onFeedback) {
      onFeedback(outputId, feedback);
      setFeedbackSubmitted(true);
      setShowFeedback(false);
    }
  };

  return (
    <div className="bg-white p-6 border border-gray-200 shadow-md rounded-lg">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">✨ Generated Output</h2>
        {!feedbackSubmitted && (
          <button 
            onClick={() => setShowFeedback(!showFeedback)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {showFeedback ? 'Cancel Feedback' : 'Give Feedback'}
          </button>
        )}
      </div>
      
      <div className="prose max-w-none">
        <pre className="whitespace-pre-wrap text-gray-800 bg-gray-50 p-4 rounded">
          {text}
        </pre>
      </div>
      
      {showFeedback && (
        <div className="mt-4 border-t pt-4">
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="What did you think of this output?"
            className="w-full p-3 border rounded resize-none"
            rows={3}
          />
          <button
            onClick={handleSubmitFeedback}
            disabled={!feedback.trim()}
            className="mt-2 bg-green-600 text-white px-4 py-2 rounded disabled:bg-gray-400"
          >
            Submit Feedback
          </button>
        </div>
      )}
      
      {feedbackSubmitted && (
        <div className="mt-4 text-sm text-green-600">
          Thanks for your feedback!
        </div>
      )}
    </div>
  );
}

export default OutputCard;