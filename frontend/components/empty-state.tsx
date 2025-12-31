"use client";

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 animate-fade-in">
      {/* Illustration */}
      <div className="relative mb-8">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-blue-500/20 rounded-full blur-3xl opacity-50 scale-150"></div>

        {/* Main icon */}
        <div className="relative bg-gradient-to-br from-gray-800 to-gray-700 border border-gray-600 rounded-3xl p-8 shadow-2xl">
          <svg
            className="w-24 h-24 text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
            />
          </svg>

          {/* Floating elements */}
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full opacity-60 animate-pulse"></div>
          <div className="absolute -bottom-2 -left-2 w-4 h-4 bg-purple-500 rounded-full opacity-60 animate-pulse" style={{ animationDelay: '0.5s' }}></div>
        </div>
      </div>

      {/* Content */}
      <div className="text-center max-w-md">
        <h3 className="text-2xl font-bold text-white mb-2">
          No tasks yet
        </h3>
        <p className="text-base text-gray-400 mb-8 leading-relaxed">
          Your task list is empty. Start organizing your work by creating your first task using the button below.
        </p>

        {/* Features */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
          <div className="flex flex-col items-center text-center p-4 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-blue-500/50 transition-colors">
            <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center mb-2">
              <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <h4 className="text-sm font-semibold text-white">Create Tasks</h4>
            <p className="text-xs text-gray-500 mt-1">Add titles and descriptions</p>
          </div>

          <div className="flex flex-col items-center text-center p-4 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-green-500/50 transition-colors">
            <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center mb-2">
              <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h4 className="text-sm font-semibold text-white">Track Progress</h4>
            <p className="text-xs text-gray-500 mt-1">Mark tasks complete</p>
          </div>

          <div className="flex flex-col items-center text-center p-4 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-purple-500/50 transition-colors">
            <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center mb-2">
              <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <h4 className="text-sm font-semibold text-white">Stay Organized</h4>
            <p className="text-xs text-gray-500 mt-1">Edit anytime you need</p>
          </div>
        </div>
      </div>
    </div>
  );
}
