'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { apiClient } from '@/lib/api';
import LifePalLogo from '@/components/LifePalLogo';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

interface Conversation {
  id: string;
  title: string;
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

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      loadConversations();
    }
  }, [user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

  const loadConversation = async (conversationId: string) => {
    try {
      const data = await apiClient.get<{
        id: string;
        title: string;
        messages: Message[];
      }>(`/api/chat/conversations/${conversationId}`);
      setMessages(data.messages);
      setCurrentConversationId(conversationId);
      setSidebarOpen(false);
    } catch (error) {
      console.error('Failed to load conversation:', error);
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

    // Add placeholder for assistant message
    const tempAssistantMessage: Message = {
      id: `temp-assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempAssistantMessage]);

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
            } else if (data.type === 'content') {
              streamingMessageRef.current += data.content;
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage && lastMessage.role === 'assistant') {
                  lastMessage.content = streamingMessageRef.current;
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

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto px-4 pb-4">
          <h3 className="text-sm font-semibold text-base-content/70 mb-4 uppercase tracking-wide">Recent Conversations</h3>
          <div className="space-y-2">
            {conversations.length === 0 ? (
              <div className="text-center py-8 text-base-content/50">
                <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p className="text-sm">No conversations yet</p>
                <p className="text-xs mt-1">Start a new chat to begin</p>
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

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-base-200 space-y-2">
          <button 
            onClick={() => router.push('/profile')}
            className="btn btn-ghost w-full justify-start gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Profile & Settings
          </button>
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
          {messages.length === 0 && !isStreaming ? (
            <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto px-4">
              <div className="mb-6">
                <LifePalLogo size="4xl" variant="default" animated={true} />
              </div>
              <h2 className="text-2xl font-bold mb-4">Welcome to LifePal!</h2>
              <p className="text-base-content/70 mb-8">Your AI-powered life assistant is here to help you organize your thoughts, track your mood, and support your wellbeing journey.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-lg">
                <div className="card bg-base-100 shadow-sm border border-base-200">
                  <div className="card-body p-4">
                    <div className="text-2xl mb-2">📝</div>
                    <h3 className="font-semibold text-sm">Write & Reflect</h3>
                    <p className="text-xs text-base-content/60">Share your thoughts and get personalized insights</p>
                  </div>
                </div>
                <div className="card bg-base-100 shadow-sm border border-base-200">
                  <div className="card-body p-4">
                    <div className="text-2xl mb-2">💭</div>
                    <h3 className="font-semibold text-sm">Daily Check-ins</h3>
                    <p className="text-xs text-base-content/60">Track your mood and wellbeing over time</p>
                  </div>
                </div>
                <div className="card bg-base-100 shadow-sm border border-base-200">
                  <div className="card-body p-4">
                    <div className="text-2xl mb-2">🎯</div>
                    <h3 className="font-semibold text-sm">Goal Setting</h3>
                    <p className="text-xs text-base-content/60">Set and track your personal goals</p>
                  </div>
                </div>
                <div className="card bg-base-100 shadow-sm border border-base-200">
                  <div className="card-body p-4">
                    <div className="text-2xl mb-2">💬</div>
                    <h3 className="font-semibold text-sm">Chat & Support</h3>
                    <p className="text-xs text-base-content/60">Get support and guidance anytime</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.filter(msg => msg.role !== 'system').map((message, index) => (
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
                        <LifePalLogo size="sm" variant="simple" />
                      )}
                    </div>
                    
                    {/* Message Content */}
                    <div className={`px-4 py-3 rounded-2xl ${
                      message.role === 'user' 
                        ? 'bg-primary text-primary-content rounded-br-md' 
                        : 'bg-base-100 border border-base-200 rounded-bl-md'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{message.content || (isStreaming && index === messages.length - 1 ? '...' : '')}</p>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Streaming message */}
              {isStreaming && (
                <div className="flex justify-start">
                  <div className="flex max-w-[80%] flex-row items-start space-x-3">
                    <div className="flex-shrink-0">
                      <LifePalLogo size="sm" variant="simple" pulse={true} />
                    </div>
                    <div className="px-4 py-3 rounded-2xl bg-base-100 border border-base-200 rounded-bl-md">
                      <div className="text-sm">
                        <div className="flex items-center space-x-1">
                          <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
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
    </div>
  );
}
