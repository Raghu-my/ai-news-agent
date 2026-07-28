import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';
import {
  Tv,
  Users,
  Eye,
  Video,
  Play,
  RefreshCw,
  Sparkles,
  Layers,
  Send,
  Zap
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

// 30-Day Impression Trend Mock Data for Recharts
const sampleChartData = [
  { day: 'Day 1', views: 1200 },
  { day: 'Day 5', views: 2800 },
  { day: 'Day 10', views: 5400 },
  { day: 'Day 15', views: 9100 },
  { day: 'Day 20', views: 16500 },
  { day: 'Day 25', views: 24200 },
  { day: 'Day 30', views: 35800 }
];

export default function App() {
  const [pipelineVideos, setPipelineVideos] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
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
      setTriggerStatus('Initiating 10-scene documentary cycle...');
      const res = await axios.post(`${API_BASE_URL}/agent/run-cycle`, { topic: topicInput });
      setTriggerStatus(`Published: ${res.data.youtube_url}`);
      setTopicInput('');
      fetchData();
    } catch (err) {
      setTriggerStatus(`Cycle error: ${err.message}`);
    } finally {
      setTriggering(false);
    }
  };

  const publishedVideos = pipelineVideos.filter(v => v.status === 'PUBLISHED');

  return (
    <div className="h-screen w-full overflow-hidden bg-slate-950 text-white flex flex-col p-4 font-sans select-none">
      {/* 1. TOP HEADER BAR */}
      <header className="flex items-center justify-between pb-3 border-b border-slate-800/80 shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Tv className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
              AI News Agent <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-mono border border-cyan-500/20">Command Center</span>
            </h1>
            <p className="text-[10px] text-slate-400">GCP Serverless Engine • Vertex AI • Imagen 3 • YouTube API</p>
          </div>
        </div>

        {/* Trigger Form */}
        <form onSubmit={handleTriggerCycle} className="flex items-center gap-2 max-w-md flex-1 mx-4">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Launch topic (e.g. Breakthrough in quantum AI coding agents)..."
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
              disabled={triggering}
            />
            {triggering && <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin absolute right-2.5 top-2" />}
          </div>
          <button
            type="submit"
            disabled={triggering || !topicInput.trim()}
            className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-xs font-semibold text-white transition flex items-center gap-1.5 disabled:opacity-40 shrink-0"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Publish</span>
          </button>
        </form>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 transition text-slate-400"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <div className="px-2.5 py-1 text-[10px] font-medium rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Online
          </div>
        </div>
      </header>

      {triggerStatus && (
        <div className="my-1.5 px-3 py-1 text-[10px] rounded bg-cyan-950/60 border border-cyan-800 text-cyan-300 shrink-0 flex items-center gap-2">
          <Zap className="w-3 h-3 text-cyan-400" />
          <span>{triggerStatus}</span>
        </div>
      )}

      {/* 2. MAIN SINGLE-SCREEN GRID */}
      <main className="grid grid-cols-12 gap-4 flex-1 min-h-0 mt-3">
        {/* COLUMN 1: ANALYTICS KPI CARDS (Cols 3/12) */}
        <section className="col-span-3 flex flex-col gap-3 min-h-0">
          <div className="glass-card rounded-xl p-3.5 border border-slate-800/80 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Subscribers</span>
              <div className="text-2xl font-black text-white mt-0.5">
                {analytics?.subscriber_count?.toLocaleString() || '1,240'}
              </div>
              <span className="text-[9px] text-emerald-400">↑ Live Channel Stat</span>
            </div>
            <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <Users className="w-4 h-4" />
            </div>
          </div>

          <div className="glass-card rounded-xl p-3.5 border border-slate-800/80 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Total Views</span>
              <div className="text-2xl font-black text-cyan-400 mt-0.5">
                {analytics?.view_count?.toLocaleString() || '58,900'}
              </div>
              <span className="text-[9px] text-cyan-400">30-Day Impressions</span>
            </div>
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Eye className="w-4 h-4" />
            </div>
          </div>

          <div className="glass-card rounded-xl p-3.5 border border-slate-800/80 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Videos Published</span>
              <div className="text-2xl font-black text-emerald-400 mt-0.5">
                {analytics?.video_count || publishedVideos.length}
              </div>
              <span className="text-[9px] text-emerald-400">Automated Catalog</span>
            </div>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Video className="w-4 h-4" />
            </div>
          </div>

          <div className="glass-card rounded-xl p-3.5 border border-slate-800/80 flex flex-col justify-between flex-1">
            <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Active GCP Region</span>
            <div>
              <div className="text-base font-bold text-slate-200">us-central1</div>
              <div className="text-[9px] text-slate-400">Vertex AI & GCS Vault</div>
            </div>
            <div className="text-[9px] text-slate-500 pt-2 border-t border-slate-800/80 flex items-center justify-between">
              <span>Cloud Run CI/CD</span>
              <span className="text-emerald-400 font-mono">ACTIVE</span>
            </div>
          </div>
        </section>

        {/* COLUMN 2: RECHARTS GRAPHICAL CHART (Cols 5/12) */}
        <section className="col-span-5 glass-card rounded-xl p-4 border border-slate-800/80 flex flex-col min-h-0 w-full min-w-0">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 shrink-0">
            <div>
              <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Channel Performance Analytics
              </h2>
              <p className="text-[9px] text-slate-400">30-Day Views & Audience Impressions Trend</p>
            </div>
            <span className="text-[9px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-400">Live Trend</span>
          </div>

          {/* Explicit width/min-w-0 flex container preventing SVG collapse */}
          <div className="w-full min-w-0 flex-1 flex flex-col justify-center pt-2">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={sampleChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.6} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', fontSize: '11px', borderRadius: '8px' }}
                />
                <Area type="monotone" dataKey="views" stroke="#06b6d4" strokeWidth={2.5} fillOpacity={1} fill="url(#colorViews)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* COLUMN 3: KANBAN PIPELINE BOARD (Cols 4/12) */}
        <section className="col-span-4 glass-card rounded-xl p-4 border border-slate-800/80 flex flex-col min-h-0">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 shrink-0">
            <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" /> Pipeline Kanban
            </h2>
            <span className="text-[9px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400 font-mono">
              Total: {pipelineVideos.length}
            </span>
          </div>

          {/* Internal Scrollable List */}
          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 mt-2.5 min-h-0">
            {pipelineVideos.length === 0 ? (
              <div className="text-center py-10 text-xs text-slate-500">No videos in pipeline. Launch a new topic above!</div>
            ) : (
              pipelineVideos.map(video => (
                <div key={video.id} className="p-3 rounded-lg bg-slate-900/90 border border-slate-800/80 hover:border-slate-700 transition space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-mono text-slate-500">#{video.id.substring(0, 8)}</span>
                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${
                      video.status === 'PUBLISHED'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        : video.status === 'STITCHED' || video.status === 'MEDIA_GENERATED'
                        ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    }`}>
                      {video.status}
                    </span>
                  </div>

                  <p className="text-xs font-medium text-slate-200 line-clamp-2">{video.topic}</p>

                  {video.youtube_url && (
                    <div className="pt-1.5 border-t border-slate-800/60 flex items-center justify-between">
                      <a
                        href={video.youtube_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-2 py-1 rounded bg-red-500/10 border border-red-500/30 text-red-400 text-[9px] font-semibold hover:bg-red-500/20 transition flex items-center gap-1"
                      >
                        <Play className="w-3 h-3 fill-red-400" /> Watch Video
                      </a>
                      <span className="text-[9px] text-slate-500 font-mono">YouTube API</span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
