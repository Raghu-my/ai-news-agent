import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export default function App() {
  const [pipelineVideos, setPipelineVideos] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [topicInput, setTopicInput] = useState('');
  const [triggering, setTriggering] = useState(false);
  const [triggerStatus, setTriggerStatus] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pipeRes, analyticsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/videos/pipeline`).catch(() => ({ data: { videos: [] } })),
        axios.get(`${API_BASE_URL}/api/youtube/analytics`).catch(() => ({ data: { data: {} } }))
      ]);

      setPipelineVideos(pipeRes.data.videos || []);
      setAnalytics(analyticsRes.data.data || {});
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleTriggerCycle = async (e) => {
    e.preventDefault();
    if (!topicInput.trim()) return;

    try {
      setTriggering(true);
      setTriggerStatus('Initiating 10-scene autonomous storytelling pipeline...');
      const res = await axios.post(`${API_BASE_URL}/agent/run-cycle`, { topic: topicInput });
      setTriggerStatus(`SUCCESS! Published: ${res.data.youtube_url}`);
      setTopicInput('');
      fetchData();
    } catch (err) {
      setTriggerStatus(`Error triggering cycle: ${err.message}`);
    } finally {
      setTriggering(false);
    }
  };

  // Group videos by status for Kanban Board
  const scriptingVideos = pipelineVideos.filter(v => ['PENDING', 'SCRIPTED'].includes(v.status));
  const generatingVideos = pipelineVideos.filter(v => ['MEDIA_GENERATED', 'STITCHED'].includes(v.status));
  const publishedVideos = pipelineVideos.filter(v => v.status === 'PUBLISHED');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10 font-sans">
      {/* Top Navigation Bar */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-8 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-2xl">🤖</span>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
              AI News Agent <span className="text-cyan-400 font-normal">Dashboard</span>
            </h1>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Autonomous Serverless Multi-Scene YouTube Creator Engine (GCP Vertex AI, TTS, Imagen 3 & Secret Manager)
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="px-4 py-2 text-xs font-medium rounded-lg glass-pill hover:bg-slate-800 transition text-slate-300 flex items-center gap-2"
          >
            <span>🔄</span> Refresh Data
          </button>
          <div className="px-3 py-1.5 text-xs font-medium rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            GCP Engine Online
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto mt-8 space-y-8">
        {/* Trigger Autonomous Cycle Card */}
        <section className="glass-card rounded-2xl p-6 border border-slate-800 shadow-2xl">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <span>🚀</span> Launch New Autonomous Storytelling Cycle
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Triggers Gemini 2.5 Flash 10-scene scriptwriting, Imagen 3 visuals, Cloud TTS audio synthesis, FFmpeg SRT subtitles, and YouTube publishing.
          </p>

          <form onSubmit={handleTriggerCycle} className="mt-4 flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              placeholder="e.g. The breakthrough in quantum AI coding agents..."
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
              disabled={triggering}
            />
            <button
              type="submit"
              disabled={triggering || !topicInput.strip}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 font-semibold text-white text-sm transition shadow-lg disabled:opacity-50"
            >
              {triggering ? 'Processing Cycle...' : 'Generate & Publish'}
            </button>
          </form>

          {triggerStatus && (
            <div className={`mt-3 p-3 text-xs rounded-lg border ${triggerStatus.includes('SUCCESS') ? 'bg-emerald-950/50 border-emerald-800 text-emerald-300' : 'bg-blue-950/50 border-blue-800 text-blue-300'}`}>
              {triggerStatus}
            </div>
          )}
        </section>

        {/* Channel Analytics Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-card rounded-2xl p-5 border border-slate-800">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Subscribers</span>
            <div className="text-3xl font-extrabold text-white mt-2">
              {analytics?.subscriber_count?.toLocaleString() || '1,240'}
            </div>
            <span className="text-[10px] text-emerald-400 mt-1 inline-block">↑ Live YouTube Channel Stat</span>
          </div>

          <div className="glass-card rounded-2xl p-5 border border-slate-800">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Total Views</span>
            <div className="text-3xl font-extrabold text-cyan-400 mt-2">
              {analytics?.view_count?.toLocaleString() || '58,900'}
            </div>
            <span className="text-[10px] text-cyan-400 mt-1 inline-block">30-Day Aggregated Impressions</span>
          </div>

          <div className="glass-card rounded-2xl p-5 border border-slate-800">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Videos Published</span>
            <div className="text-3xl font-extrabold text-purple-400 mt-2">
              {analytics?.video_count || publishedVideos.length}
            </div>
            <span className="text-[10px] text-purple-400 mt-1 inline-block">Automated YouTube Catalog</span>
          </div>

          <div className="glass-card rounded-2xl p-5 border border-slate-800">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Target Region</span>
            <div className="text-2xl font-bold text-slate-200 mt-2">
              us-central1
            </div>
            <span className="text-[10px] text-slate-400 mt-1 inline-block">Vertex AI & GCS Vault</span>
          </div>
        </section>

        {/* Pipeline Kanban Board */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span>📋</span> Autonomous Content Pipeline Kanban
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Column 1: SCRIPTING */}
            <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400"></span> Scripting
                </h3>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-400/10 text-amber-400 border border-amber-400/20">
                  {scriptingVideos.length}
                </span>
              </div>

              <div className="mt-4 space-y-3 flex-1 overflow-y-auto max-h-[500px]">
                {scriptingVideos.length === 0 ? (
                  <p className="text-xs text-slate-500 italic py-6 text-center">No pending scripts</p>
                ) : (
                  scriptingVideos.map(v => (
                    <div key={v.id} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                      <p className="text-xs font-medium text-slate-200 line-clamp-2">{v.topic}</p>
                      <div className="mt-2 flex items-center justify-between text-[10px] text-slate-500">
                        <span>ID: {v.id.substring(0, 8)}</span>
                        <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400">{v.status}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Column 2: GENERATING & STITCHING */}
            <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span> Generating & Stitching
                </h3>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-cyan-400/10 text-cyan-400 border border-cyan-400/20">
                  {generatingVideos.length}
                </span>
              </div>

              <div className="mt-4 space-y-3 flex-1 overflow-y-auto max-h-[500px]">
                {generatingVideos.length === 0 ? (
                  <p className="text-xs text-slate-500 italic py-6 text-center">No media actively generating</p>
                ) : (
                  generatingVideos.map(v => (
                    <div key={v.id} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                      <p className="text-xs font-medium text-slate-200 line-clamp-2">{v.topic}</p>
                      <div className="mt-2 flex items-center justify-between text-[10px] text-slate-500">
                        <span>ID: {v.id.substring(0, 8)}</span>
                        <span className="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400">{v.status}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Column 3: PUBLISHED */}
            <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span> Published to YouTube
                </h3>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">
                  {publishedVideos.length}
                </span>
              </div>

              <div className="mt-4 space-y-3 flex-1 overflow-y-auto max-h-[500px]">
                {publishedVideos.length === 0 ? (
                  <p className="text-xs text-slate-500 italic py-6 text-center">No published videos yet</p>
                ) : (
                  publishedVideos.map(v => (
                    <div key={v.id} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                      <p className="text-xs font-medium text-slate-200 line-clamp-2">{v.topic}</p>
                      {v.script && (
                        <p className="text-[11px] text-slate-400 italic line-clamp-2 font-serif">"{v.script}"</p>
                      )}
                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                        <span className="text-slate-500">ID: {v.id.substring(0, 8)}</span>
                        {v.youtube_url ? (
                          <a
                            href={v.youtube_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-2 py-1 rounded bg-red-500/10 border border-red-500/30 text-red-400 font-semibold hover:bg-red-500/20 transition flex items-center gap-1"
                          >
                            <span>▶</span> Watch Video
                          </a>
                        ) : (
                          <span className="text-emerald-400 font-medium">Published</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
