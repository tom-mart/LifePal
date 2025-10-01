'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { apiClient } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
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
  const { theme, setTheme, availableThemes } = useTheme();
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
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-80 bg-base-200 border-r border-base-300 transition-transform duration-300 ease-in-out flex flex-col`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-base-300 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src="/LifePal-Main-TransparentBG.png"
              alt="LifePal"
              width={40}
              height={40}
              className="opacity-90 dark:invert"
              style={{ filter: 'var(--logo-filter, none)' }}
            />
            <span className="text-xl font-bold">LifePal</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="btn btn-ghost btn-sm btn-square lg:hidden"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
        <div className="flex-1 overflow-y-auto px-2">
          {conversations.map((conv) => (
            <div key={conv.id} className="relative group mb-1">
              <button
                onClick={() => loadConversation(conv.id)}
                className={`btn btn-ghost w-full justify-start text-left h-auto py-3 px-3 ${
                  currentConversationId === conv.id ? 'bg-base-300' : ''
                }`}
              >
                <div className="flex-1 truncate pr-8">
                  <div className="font-medium truncate">{conv.title}</div>
                  <div className="text-xs opacity-60">
                    {new Date(conv.updated_at).toLocaleDateString()}
                  </div>
                </div>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm('Delete this conversation?')) {
                    deleteConversation(conv.id);
                  }
                }}
                className="btn btn-ghost btn-xs btn-square absolute right-2 top-1/2 -translate-y-1/2 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 transition-opacity text-error"
                title="Delete conversation"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ))}
        </div>

        {/* User Menu at Bottom */}
        <div className="p-4 border-t border-base-300">
          <div className="dropdown dropdown-top dropdown-end w-full">
            <label tabIndex={0} className="btn btn-ghost w-full justify-start gap-3">
              <div className="avatar placeholder">
                <div className="bg-primary text-primary-content rounded-full w-10">
                  <span className="text-lg">{user.username[0].toUpperCase()}</span>
                </div>
              </div>
              <div className="flex-1 text-left truncate">
                <div className="font-medium truncate">{user.username}</div>
              </div>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
            </label>
            <ul tabIndex={0} className="dropdown-content menu p-2 shadow-lg bg-base-100 rounded-box w-full mb-2">
              <li><Link href="/profile">Profile</Link></li>
              <li><Link href="/settings">Settings</Link></li>
              <li><Link href="/context">AI Context</Link></li>
              <li className="border-t border-base-300 mt-1 pt-1">
                <button onClick={logout} className="text-error">Logout</button>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen">
        {/* Top Bar */}
        <div className="navbar bg-base-100 border-b border-base-300 flex-none">
          <button
            onClick={() => setSidebarOpen(true)}
            className="btn btn-ghost btn-square lg:hidden"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="flex-1">
            <span className="text-lg font-semibold">Chat</span>
          </div>
          <div className="dropdown dropdown-end">
            <label tabIndex={0} className="btn btn-ghost btn-circle">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </label>
            <ul tabIndex={0} className="dropdown-content z-[100] menu bg-base-100 border border-base-300 rounded-box w-56 shadow-2xl mt-2 max-h-96 overflow-y-auto">
              {availableThemes.map((t) => (
                <li key={t} className="w-full">
                  <button
                    className={`${theme === t ? 'active' : ''} w-full text-left whitespace-nowrap`}
                    onClick={() => setTheme(t)}
                  >
                    {t}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-lg px-4">
                <Image
                  src="/LifePal-Main-TransparentBG.png"
                  alt="LifePal"
                  width={120}
                  height={120}
                  className="mx-auto mb-6 opacity-80 dark:invert"
                  style={{ filter: 'var(--logo-filter, none)' }}
                />
                <h2 className="text-3xl font-bold mb-3">Welcome to LifePal!</h2>
                <p className="text-base-content/70 mb-8">Your AI assistant is ready to help. Start a conversation by typing a message below.</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <div className="badge badge-lg gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Real-time
                  </div>
                  <div className="badge badge-lg gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    Secure
                  </div>
                  <div className="badge badge-lg gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Private
                  </div>
                </div>
              </div>
            </div>
          ) : (
              messages.map((message, index) => (
                <div key={message.id || index} className={`chat ${message.role === 'user' ? 'chat-end' : 'chat-start'}`}>
                  <div className="chat-image avatar placeholder">
                    <div className={`w-10 rounded-full ${message.role === 'user' ? 'bg-primary text-primary-content' : 'bg-secondary text-secondary-content'}`}>
                      {message.role === 'user' ? (
                        <span className="text-lg font-bold">{user.username[0].toUpperCase()}</span>
                      ) : (
                        <span className="text-lg">🤖</span>
                      )}
                    </div>
                  </div>
                  <div className={`chat-bubble ${message.role === 'user' ? 'chat-bubble-primary' : ''} max-w-[85%] md:max-w-2xl`}>
                    {message.content || (isStreaming && index === messages.length - 1 ? <span className="loading loading-dots loading-sm"></span> : '')}
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

        {/* Input Area - Fixed at Bottom */}
        <div className="border-t border-base-300 p-4 bg-base-100 flex-none">
          <form onSubmit={handleSendMessage} className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              placeholder="Type your message..."
              className="input input-bordered flex-1"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isStreaming}
            />
            <button
              type="submit"
              className={`btn btn-primary ${isStreaming ? 'loading' : ''}`}
              disabled={isStreaming || !input.trim()}
            >
              {!isStreaming && (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
