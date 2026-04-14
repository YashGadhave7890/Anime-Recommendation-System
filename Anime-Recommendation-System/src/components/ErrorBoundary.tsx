import React, { ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';
import { Button } from './ui/button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex flex-col items-center justify-center py-20 px-6 text-center space-y-6 bg-white/5 rounded-3xl border border-dashed border-white/10 animate-fade-in">
          <div className="inline-flex p-6 rounded-full bg-destructive/10 border border-destructive/20">
            <AlertTriangle className="text-destructive" size={40} />
          </div>
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-white">Something went wrong</h2>
            <p className="text-muted-foreground max-w-xs mx-auto text-sm">
              We encountered an error while rendering the recommendations.
            </p>
          </div>
          <Button 
            onClick={this.handleReset}
            variant="outline" 
            className="rounded-full border-white/10 hover:bg-white/5 gap-2"
          >
            <RefreshCcw size={16} /> Try Again
          </Button>
          <pre className="mt-4 p-4 bg-black/50 rounded-lg text-left text-xs text-destructive overflow-auto max-w-full">
            {this.state.error?.toString()}
          </pre>
        </div>
      );
    }

    return this.props.children;
  }
}
