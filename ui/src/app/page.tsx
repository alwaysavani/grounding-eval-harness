"use client";

import { useState } from "react";

export default function Home() {
  const [baseResume, setBaseResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [outputFormat, setOutputFormat] = useState("Markdown");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/tailor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          base_resume_text: baseResume,
          job_description_text: jobDescription,
          output_format: outputFormat,
        }),
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
          Grounded Eval Harness Demo
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
              <h2 className="text-xl font-semibold mb-4 text-gray-200">Input Data</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Base Resume</label>
                  <textarea
                    className="w-full h-48 bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                    placeholder="Paste your source-of-truth resume here..."
                    value={baseResume}
                    onChange={(e) => setBaseResume(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Job Description</label>
                  <textarea
                    className="w-full h-48 bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                    placeholder="Paste the job description here..."
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Output Format</label>
                  <select
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    value={outputFormat}
                    onChange={(e) => setOutputFormat(e.target.value)}
                  >
                    <option value="Markdown">Markdown</option>
                    <option value="LaTeX">LaTeX</option>
                  </select>
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full py-3 rounded-lg font-bold text-white transition-all ${
                    loading ? "bg-blue-600/50 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-500 shadow-[0_0_15px_rgba(37,99,235,0.5)]"
                  }`}
                >
                  {loading ? "Processing Pipeline..." : "Tailor Resume"}
                </button>
              </form>
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg flex flex-col">
            <h2 className="text-xl font-semibold mb-4 text-gray-200">Results</h2>
            
            {error && (
              <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg mb-4">
                {error}
              </div>
            )}

            {!result && !loading && !error && (
              <div className="flex-1 flex items-center justify-center text-gray-500 italic">
                Awaiting input...
              </div>
            )}

            {loading && (
              <div className="flex-1 flex flex-col items-center justify-center space-y-4">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-blue-400 animate-pulse">Running Agentic LangGraph Pipeline...</p>
              </div>
            )}

            {result && !loading && (
              <div className="flex-1 flex flex-col space-y-4 overflow-y-auto">
                <div className={`p-4 rounded-lg border ${result.hallucinations_found ? "bg-yellow-900/30 border-yellow-600" : "bg-emerald-900/30 border-emerald-600"}`}>
                  <h3 className={`font-bold ${result.hallucinations_found ? "text-yellow-400" : "text-emerald-400"}`}>
                    {result.hallucinations_found ? "⚠️ Hallucinations Corrected" : "✅ Perfectly Grounded"}
                  </h3>
                  <p className="text-sm mt-1 text-gray-300">Iterations taken: {result.iteration_count}</p>
                  {result.evaluation_feedback && (
                    <div className="mt-2 text-sm bg-black/30 p-2 rounded text-gray-300">
                      {result.evaluation_feedback}
                    </div>
                  )}
                </div>

                <div className={`flex-1 bg-gray-900 border border-gray-700 rounded-lg p-4 overflow-y-auto font-mono ${outputFormat === "LaTeX" ? "text-xs text-blue-300" : "text-sm text-gray-300"} whitespace-pre-wrap`}>
                  <div className="text-gray-500 mb-2 border-b border-gray-700 pb-2 font-sans font-bold">
                    {outputFormat === "LaTeX" ? "LaTeX Code Block" : "Tailored Resume (Markdown)"}
                  </div>
                  {result.draft_resume}
                </div>

                {result.agent_notes && (
                  <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 font-sans text-sm text-gray-300 whitespace-pre-wrap mt-4">
                    <div className="text-gray-500 mb-2 border-b border-gray-700 pb-2 font-bold">Additional Agent Notes</div>
                    {result.agent_notes}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
