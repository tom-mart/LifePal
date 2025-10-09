'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { apiClient } from '@/lib/api';
import LifePalLogo from '@/components/LifePalLogo';
import MarkdownMessage from '@/components/MarkdownMessage';
import PWAInstallPrompt from '@/components/PWAInstallPrompt';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'trigger';
  content: string;
  created_at: string;
}

interface Conversation {
  id: string;
  title: string;
  conversation_type: 'general' | 'checkin';
  created_at: string;
  updated_at: string;
}

export default function ChatPage() {
  const { user, loading: authLoading, logout } = useAuth();
  const { theme, setTheme, themeConfig } = useTheme();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const streamingMessageRef = useRef<string>('');
  const lastActivityRef = useRef<number>(Date.now());
  const inactivityCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const [checkinId, setCheckinId] = useState<string | null>(null);
  const [isCheckinMode, setIsCheckinMode] = useState(false);
  const [checkinComplete, setCheckinComplete] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      loadConversations();
      
      // Check for check-in parameter in URL
      const urlParams = new URLSearchParams(window.location.search);
      const checkinIdParam = urlParams.get('checkin_id');
      
      if (checkinIdParam) {
        setCheckinId(checkinIdParam);
        setIsCheckinMode(true);
        startCheckin(checkinIdParam);
      }
    }
  }, [user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Inactivity check - start new chat after 15 minutes of inactivity
  useEffect(() => {
    const INACTIVITY_TIMEOUT = 15 * 60 * 1000; // 15 minutes in milliseconds

    const checkInactivity = () => {
      const now = Date.now();
      const timeSinceLastActivity = now - lastActivityRef.current;
      
      if (timeSinceLastActivity >= INACTIVITY_TIMEOUT && currentConversationId) {
        console.log('Starting new chat due to inactivity');
        startNewConversation();
      }
    };

    // Update last activity on user interactions
    const updateActivity = () => {
      lastActivityRef.current = Date.now();
    };

    // Track various user activities
    window.addEventListener('mousedown', updateActivity);
    window.addEventListener('keydown', updateActivity);
    window.addEventListener('touchstart', updateActivity);
    window.addEventListener('scroll', updateActivity);

    // Check for inactivity every minute
    inactivityCheckIntervalRef.current = setInterval(checkInactivity, 60 * 1000);

    // Cleanup
    return () => {
      window.removeEventListener('mousedown', updateActivity);
      window.removeEventListener('keydown', updateActivity);
      window.removeEventListener('touchstart', updateActivity);
      window.removeEventListener('scroll', updateActivity);
      if (inactivityCheckIntervalRef.current) {
        clearInterval(inactivityCheckIntervalRef.current);
      }
    };
  }, [currentConversationId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      const data = await apiClient.get<{ conversations: Conversation[] }>('/api/chat/conversations');
      setConversations(data.conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const startCheckin = async (checkinIdParam: string) => {
    try {
      const response = await apiClient.post<{
        success: boolean;
        conversation_id: string;
        checkin_id: string;
        checkin_type: string;
        already_started?: boolean;
      }>(`/api/wellbeing/checkins/${checkinIdParam}/start`, {});
      
      if (response.success) {
        setCurrentConversationId(response.conversation_id);
        setCheckinId(response.checkin_id);
        setIsCheckinMode(true);
        
        // Don't clear URL yet - wait until check-in is complete
        // This allows proper state restoration on refresh
        
        if (response.already_started) {
          // Load existing conversation
          loadConversation(response.conversation_id);
        } else {
          // New check-in: Auto-send trigger message to initiate LLM interaction
          // The LLM will use Tool_Retriever to discover and call start_checkin tool
          const triggerMessages: Record<string, string> = {
            'morning': 'I want to start my morning check-in',
            'midday': 'I want to do a midday check-in',
            'evening': 'I want to start my evening reflection',
            'adhoc': 'I want to do a check-in'
          };
          
          const triggerMessage = triggerMessages[response.checkin_type] || 'I want to start my check-in';
          
          // Auto-send the trigger message
          // This will cause the LLM to call Tool_Retriever → start_checkin → generate opening
          setInput(triggerMessage);
          
          // Trigger the send immediately
          setTimeout(() => {
            const form = document.querySelector('form');
            if (form) {
              form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
            }
          }, 100);
        }
      }
    } catch (error) {
      console.error('Failed to start check-in:', error);
    }
  };

  const loadConversation = async (conversationId: string) => {
    try {
      const data = await apiClient.get<{
        id: string;
        title: string;
        messages: Message[];
      }>(`/api/chat/conversations/${conversationId}`);
      
      // Filter out system and trigger messages from display
      const displayMessages = (data.messages || []).filter(
        msg => msg.role !== 'system' && msg.role !== 'trigger'
      );
      setMessages(displayMessages);
      setCurrentConversationId(conversationId);
      setSidebarOpen(false);
      lastActivityRef.current = Date.now();
    } catch (error: any) {
      console.error('Failed to load conversation:', conversationId, error);
      // Still set the conversation as active even if loading fails
      setMessages([]);
      setCurrentConversationId(conversationId);
      setSidebarOpen(false);
    }
  };

  const deleteConversation = async (conversationId: string) => {
    try {
      await apiClient.delete(`/api/chat/conversations/${conversationId}`);
      if (currentConversationId === conversationId) {
        setMessages([]);
        setCurrentConversationId(null);
      }
      loadConversations();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setCurrentConversationId(null);
    setSidebarOpen(false);
    lastActivityRef.current = Date.now(); // Update activity timestamp
    // Clear check-in mode if active
    setIsCheckinMode(false);
    setCheckinId(null);
    setCheckinComplete(false);
  };

  const exitCheckinMode = () => {
    // Clear check-in state and start fresh conversation
    setIsCheckinMode(false);
    setCheckinId(null);
    setCheckinComplete(false);
    setMessages([]);
    setCurrentConversationId(null);
    // Remove checkin_id from URL
    window.history.replaceState({}, '', '/chat');
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to UI
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);

    setIsStreaming(true);
    streamingMessageRef.current = '';
    lastActivityRef.current = Date.now(); // Update activity timestamp

    try {
      const stream = await apiClient.streamPost('/api/chat/send/stream', {
        message: userMessage,
        conversation_id: currentConversationId,
      });

      const reader = stream.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter((line) => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);

            if (data.type === 'start') {
              if (!currentConversationId) {
                setCurrentConversationId(data.conversation_id);
              }
            } else if (data.type === 'tool_call') {
              // Tool is being called (optional: show status to user)
              console.log('Tool called:', data.name, data.parameters);
              // Could show a loading indicator here: "Fetching your tasks..."
            } else if (data.type === 'tool_result') {
              // Tool execution completed (optional: log result)
              console.log('Tool result:', data.name, data.result);
            } else if (data.type === 'tools_discovered') {
              // Tool_Retriever returned new tools (optional: log)
              console.log('Tools discovered:', data.count, data.tools);
            } else if (data.type === 'content') {
              streamingMessageRef.current += data.content;
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage && lastMessage.role === 'assistant') {
                  lastMessage.content = streamingMessageRef.current;
                } else {
                  // Create assistant message if it doesn't exist
                  newMessages.push({
                    id: `temp-assistant-${Date.now()}`,
                    role: 'assistant',
                    content: streamingMessageRef.current,
                    created_at: new Date().toISOString(),
                  });
                }
                return newMessages;
              });
            } else if (data.type === 'end') {
              // Update with final message data
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage && lastMessage.role === 'assistant') {
                  lastMessage.id = data.message.id;
                  lastMessage.content = data.message.content;
                  lastMessage.created_at = data.message.created_at;
                }
                return newMessages;
              });
              
              // Check if check-in was completed
              if (data.checkin_complete) {
                setCheckinComplete(true);
                console.log('Check-in completed with insights:', data.checkin_insights);
                
                // Clear checkin_id from URL now that it's complete
                window.history.replaceState({}, '', '/chat');
                
                // Auto-exit check-in mode after a delay
                setTimeout(() => {
                  exitCheckinMode();
                }, 3000); // 3 seconds to see the success message
              }
              
              loadConversations();
            }
          } catch (error) {
            console.error('Failed to parse streaming data:', error);
          }
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.role === 'assistant') {
          lastMessage.content = 'Sorry, I encountered an error. Please try again.';
        }
        return newMessages;
      });
    } finally {
      setIsStreaming(false);
      streamingMessageRef.current = '';
    }
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <span className="loading loading-spinner loading-lg text-primary"></span>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-base-200">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:relative z-30 w-80 h-full bg-base-100 shadow-xl transition-transform duration-300 ease-in-out flex flex-col border-r border-base-200`}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-6 border-b border-base-200 bg-gradient-to-r from-primary/5 to-secondary/5">
          <div className="flex items-center space-x-3">
            <LifePalLogo size="md" variant="gradient" />
            <div>
              <h1 className="font-bold text-lg text-base-content">LifePal</h1>
              <p className="text-xs text-base-content/60">AI Life Assistant</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden btn btn-ghost btn-sm btn-circle hover:bg-base-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-4">
          <button onClick={startNewConversation} className="btn btn-primary w-full gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Sidebar Content */}
        <div className="flex-1 overflow-y-auto px-4 pb-4">
          {/* Quick Actions */}
          <div className="mb-4 space-y-2">
            <button 
              onClick={() => router.push('/files')}
              className="btn btn-ghost w-full justify-start gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Files
            </button>
            <button 
              onClick={() => router.push('/profile')}
              className="btn btn-ghost w-full justify-start gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Profile & Settings
            </button>
          </div>

          <div className="divider my-2"></div>

          {/* Collapsible History */}
          <details className="collapse collapse-arrow bg-base-200/50 rounded-box">
            <summary className="collapse-title text-sm font-semibold text-base-content/70 uppercase tracking-wide min-h-0 py-3">
              Recent Conversations
            </summary>
            <div className="collapse-content px-2">
              <div className="space-y-2 mt-2">
                {conversations.length === 0 ? (
                  <div className="text-center py-6 text-base-content/50">
                    <svg className="w-10 h-10 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <p className="text-xs">No conversations yet</p>
                  </div>
                ) : (
                  conversations.map((conv) => (
                    <div
                      key={conv.id}
                      className={`group relative p-3 rounded-xl cursor-pointer transition-all duration-200 ${
                        currentConversationId === conv.id 
                          ? 'bg-primary/10 border border-primary/20 shadow-sm' 
                          : 'hover:bg-base-200/70 hover:shadow-sm'
                      }`}
                      onClick={() => loadConversation(conv.id)}
                    >
                      <div className="pr-8">
                        <div className="font-medium text-sm truncate mb-1">{conv.title}</div>
                        <div className="text-xs text-base-content/50">
                          {new Date(conv.updated_at).toLocaleDateString(undefined, { 
                            month: 'short', 
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm('Delete this conversation?')) {
                            deleteConversation(conv.id);
                          }
                        }}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-error/20 rounded-lg"
                        title="Delete conversation"
                      >
                        <svg className="w-3.5 h-3.5 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </details>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-base-200 space-y-2">
          <button 
            onClick={logout}
            className="btn btn-ghost w-full justify-start gap-2 text-error"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Mobile Header - Fixed positioning */}
        <div className="lg:hidden sticky top-0 z-10 flex items-center justify-between p-3 bg-base-100/95 backdrop-blur-sm border-b border-base-200 shadow-sm">
          <button 
            onClick={() => setSidebarOpen(true)}
            className="btn btn-ghost btn-sm btn-circle"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="flex items-center space-x-2">
            <LifePalLogo size="sm" variant="simple" />
            <span className="font-semibold text-base">LifePal</span>
          </div>
          <div className="flex items-center space-x-1">
            {currentConversationId && (
              <button 
                onClick={startNewConversation}
                className="btn btn-ghost btn-sm btn-circle"
                title="Close conversation"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
            <div className="dropdown dropdown-end">
            <label tabIndex={0} className="btn btn-ghost btn-sm btn-circle">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </label>
            <ul tabIndex={0} className="dropdown-content z-[100] menu p-2 bg-base-100 border border-base-300 rounded-box w-64 shadow-2xl mt-2 max-h-[70vh] overflow-y-auto" style={{display: 'block'}}>
              <li className="menu-title">
                <span className="text-xs font-semibold uppercase tracking-wider">Choose Theme</span>
              </li>
              {themeConfig.map((t) => (
                <li key={t.name} style={{width: '100%'}}>
                  <button
                    className={`flex items-center gap-3 py-3 w-full ${theme === t.name ? 'active bg-primary/10' : ''}`}
                    onClick={() => setTheme(t.name as any)}
                  >
                    <span className="text-2xl">{t.icon}</span>
                    <div className="flex-1 text-left">
                      <div className="font-medium capitalize">{t.name}</div>
                      <div className="text-xs text-base-content/60">{t.description}</div>
                    </div>
                    {theme === t.name && (
                      <svg className="w-4 h-4 text-primary" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>
                </li>
              ))}
            </ul>
            </div>
          </div>
        </div>

        {/* Desktop Header */}
        <div className="hidden lg:flex items-center justify-between p-4 bg-base-100 border-b border-base-200">
          <div className="flex items-center space-x-2">
            <span className="text-lg font-semibold">Chat</span>
            {currentConversationId && (
              <span className="text-sm text-base-content/60">
                • {conversations.find(c => c.id === currentConversationId)?.title || 'Conversation'}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {currentConversationId && (
              <button 
                onClick={startNewConversation}
                className="btn btn-ghost btn-sm gap-2"
                title="Close conversation"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Close
              </button>
            )}
            <div className="dropdown dropdown-end">
              <label tabIndex={0} className="btn btn-ghost btn-sm gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
                <span className="hidden xl:inline">Theme</span>
              </label>
              <ul tabIndex={0} className="dropdown-content z-[100] menu p-2 bg-base-100 border border-base-300 rounded-box w-64 shadow-2xl mt-2 max-h-[70vh] overflow-y-auto" style={{display: 'block'}}>
                <li className="menu-title">
                  <span className="text-xs font-semibold uppercase tracking-wider">Choose Theme</span>
                </li>
                {themeConfig.map((t) => (
                  <li key={t.name} style={{width: '100%'}}>
                    <button
                      className={`flex items-center gap-3 py-3 w-full ${theme === t.name ? 'active bg-primary/10' : ''}`}
                      onClick={() => setTheme(t.name as any)}
                    >
                      <span className="text-2xl">{t.icon}</span>
                      <div className="flex-1 text-left">
                        <div className="font-medium capitalize">{t.name}</div>
                        <div className="text-xs text-base-content/60">{t.description}</div>
                      </div>
                      {theme === t.name && (
                        <svg className="w-4 h-4 text-primary" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <button 
              onClick={startNewConversation}
              className="btn btn-ghost btn-sm gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 pb-0">
          {/* Check-in Mode Indicator */}
          {isCheckinMode && !checkinComplete && (
            <div className="max-w-4xl mx-auto mb-4">
              <div className="alert alert-info">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>You're in a check-in session. The conversation will be saved to your daily log.</span>
              </div>
            </div>
          )}
          
          {/* Check-in Complete Indicator */}
          {checkinComplete && (
            <div className="max-w-4xl mx-auto mb-4">
              <div className="alert alert-success">
                <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="flex-1">
                  <span>Check-in complete! Your insights have been saved.</span>
                </div>
                <button 
                  onClick={exitCheckinMode}
                  className="btn btn-sm btn-ghost"
                >
                  Start New Chat
                </button>
              </div>
            </div>
          )}
          
          {messages.length === 0 && !isStreaming ? (
            <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto px-4 pt-8">
              <div className="mb-8 mt-4">
                <LifePalLogo size="4xl" variant="simple" animated={true} />
              </div>
              <h2 className="text-2xl font-bold mb-3">Welcome to LifePal!</h2>
              <p className="text-base-content/70 mb-6">Your AI-powered life assistant is here to help you organize your thoughts, track your mood, and support your wellbeing journey.</p>
              
              <div className="flex flex-wrap gap-3 justify-center w-full max-w-md">
                <div className="badge badge-lg gap-2 py-4 px-4">
                  <span className="text-lg">📝</span>
                  <span className="text-sm">Write & Reflect</span>
                </div>
                <div className="badge badge-lg gap-2 py-4 px-4">
                  <span className="text-lg">💭</span>
                  <span className="text-sm">Daily Check-ins</span>
                </div>
                <div className="badge badge-lg gap-2 py-4 px-4">
                  <span className="text-lg">🎯</span>
                  <span className="text-sm">Goal Setting</span>
                </div>
                <div className="badge badge-lg gap-2 py-4 px-4">
                  <span className="text-lg">💬</span>
                  <span className="text-sm">Chat & Support</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.filter(msg => msg.role !== 'system' && msg.role !== 'trigger').map((message, index) => (
                <div
                  key={message.id || index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
                    {/* Avatar */}
                    <div className="flex-shrink-0">
                      {message.role === 'user' ? (
                        <div className="w-8 h-8 rounded-full bg-primary text-primary-content flex items-center justify-center text-sm font-semibold">
                          {user?.username?.[0]?.toUpperCase() || 'U'}
                        </div>
                      ) : (
                        <LifePalLogo size="md" variant="simple" />
                      )}
                    </div>
                    
                    {/* Message Content */}
                    <div className={`px-4 py-3 rounded-2xl ${
                      message.role === 'user' 
                        ? 'bg-primary text-primary-content rounded-br-md' 
                        : 'bg-base-100 border border-base-200 rounded-bl-md'
                    }`}>
                      {message.content ? (
                        <MarkdownMessage 
                          content={message.content} 
                          isUser={message.role === 'user'}
                        />
                      ) : (
                        isStreaming && index === messages.length - 1 && (
                          <div className="flex items-center space-x-1 text-base-content/50">
                            <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              
              <div ref={messagesEndRef} />
            </div>
          )}

        </div>

        {/* Input Area - Fixed to bottom with safe area */}
        <div className="sticky bottom-0 bg-base-100 border-t border-base-200 p-4 pb-safe">
          <div className="max-w-4xl mx-auto">
            <form onSubmit={handleSendMessage} className="flex items-end space-x-2 sm:space-x-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your message..."
                  className="input input-bordered w-full pr-3"
                  disabled={isStreaming}
                />
              </div>
              
              <button
                type="submit"
                className={`btn btn-primary btn-circle flex-shrink-0 ${isStreaming ? 'loading' : ''}`}
                disabled={isStreaming || !input.trim()}
              >
                {!isStreaming && (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* PWA Install Prompt */}
      <PWAInstallPrompt />
    </div>
  );
}
