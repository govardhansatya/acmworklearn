import React, { useState } from 'react';

function InputBox({ onSubmit, loading }) {
  const [input, setInput] = useState('');
  const [type, setType] = useState('poetry');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSubmit(input, type);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6 space-y-4">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        rows="5"
        className="w-full border border-gray-300 rounded p-3"
        placeholder="Describe your creative idea or ask it to continue..."
      />
      <div className="flex justify-between items-center">
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="border p-2 rounded"
        >
          <option value="poetry">Poetry</option>
          <option value="melody">Melody</option>
          <option value="script">Game Script</option>
        </select>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </div>
    </form>
  );
}

export default InputBox;
