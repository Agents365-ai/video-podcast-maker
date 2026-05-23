import React from "react";
import type { VideoProps } from "../Root";

interface ErrorBoundaryProps {
  props: VideoProps;
  sectionName?: string;
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(p: ErrorBoundaryProps) {
    super(p);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  render() {
    if (!this.state.hasError) return this.props.children;

    const { props, sectionName } = this.props;
    const v = props.orientation === "vertical";

    return (
      <div style={{
        width: "100%",
        height: "100%",
        background: props.backgroundColor,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: v ? "60px 40px" : "80px 60px",
        boxSizing: "border-box",
      }}>
        <div style={{
          fontSize: v ? 48 : 56,
          fontWeight: 700,
          color: props.primaryColor,
          marginBottom: 24,
        }}>
          {sectionName || "Section"}
        </div>
        <div style={{
          fontSize: v ? 24 : 28,
          color: props.textColor,
          opacity: 0.5,
          textAlign: "center",
        }}>
          Render error: {this.state.error?.message || "Unknown"}
        </div>
      </div>
    );
  }
}
