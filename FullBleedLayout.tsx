/**
 * FullBleed Layout System for Remotion
 *
 * 硬约束布局系统 — 所有组件强制铺满屏幕，杜绝"留白/缩中间"问题
 *
 * 使用方法：
 * 1. 复制此文件到项目 src/remotion/ 目录
 * 2. 每个 Section 必须用 <FullBleed> 包裹
 * 3. 图片/视频必须用 <CoverMedia> 渲染
 * 4. 非 16:9 素材必须用 <DualLayerMedia> (模糊背景 + 清晰前景)
 *
 * NOTE: 此文件需要在有 remotion 和 react 依赖的项目中使用
 */
// @ts-nocheck
import { AbsoluteFill, Img, Video, useCurrentFrame, useVideoConfig, interpolate, Easing } from 'remotion'
import React from 'react'

// ============================================================
// 设计令牌 — 统一全局配置
// ============================================================

// ⬜ 简约纯白 (默认风格)
export const tokens = {
  colors: {
    bg: '#fff',
    text: '#1a1a1a',
    textMuted: 'rgba(0,0,0,0.5)',
    accent: '#2563eb',
    positive: '#059669',
    negative: '#dc2626',
    orange: '#ea580c',
  },
  // 字号 (1080p 基准，4K 渲染时 scale(2) 自动放大)
  fontSize: {
    hero: 100,      // Hero 主标题
    title: 80,      // 章节标题
    subtitle: 56,   // 副标题
    body: 40,       // 正文
    caption: 32,    // 说明文字
    dataLarge: 120, // 超大数据
    data: 72,       // 数据数字
  },
  // 间距
  spacing: {
    page: 40,       // 页面边距 (极窄)
    section: 50,    // 章节间距
    element: 30,    // 元素间距
    tight: 16,      // 紧凑间距
  },
  // 尺寸约束
  layout: {
    minContentWidth: 0.85,  // 内容最小宽度 (屏幕 85%)
    maxContentWidth: 0.95,  // 内容最大宽度 (屏幕 95%)
    cardWidth: 1000,        // 卡片宽度 (1080p)
    subtitleMargin: 100,    // 底部字幕留白
  },
}

// 🌙 深色科技风 (备选)
export const darkTokens = {
  colors: {
    bg: '#0a0a0f',
    bgCard: 'rgba(255,255,255,0.05)',
    text: '#ffffff',
    textMuted: 'rgba(255,255,255,0.6)',
    accent: '#00d4ff',
    accentPurple: '#a855f7',
    positive: '#22c55e',
    negative: '#ef4444',
  },
  fontSize: tokens.fontSize,
  spacing: tokens.spacing,
  layout: tokens.layout,
}

// 🎨 渐变活力风 (备选)
export const gradientTokens = {
  colors: {
    bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    bgWarm: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    bgCool: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    text: '#ffffff',
    textMuted: 'rgba(255,255,255,0.8)',
    accent: '#ffd700',
    positive: '#22c55e',
    negative: '#ef4444',
  },
  fontSize: tokens.fontSize,
  spacing: tokens.spacing,
  layout: tokens.layout,
}

// ============================================================
// FullBleed — 强制铺满的根容器
// ============================================================

interface FullBleedProps {
  children: React.ReactNode
  background?: string
  style?: React.CSSProperties
}

/**
 * 强制铺满屏幕的容器
 *
 * 硬约束：
 * - position: absolute + inset: 0
 * - overflow: hidden
 * - padding/margin: 0
 *
 * 所有 Section 必须用此组件包裹
 */
export const FullBleed: React.FC<FullBleedProps> = ({
  children,
  background = tokens.colors.bg,
  style,
}) => (
  <AbsoluteFill
    style={{
      position: 'absolute',
      inset: 0,
      overflow: 'hidden',
      padding: 0,
      margin: 0,
      background,
      ...style,
    }}
  >
    {children}
  </AbsoluteFill>
)

// ============================================================
// ContentArea — 内容区域 (自动居中但宽度受控)
// ============================================================

interface ContentAreaProps {
  children: React.ReactNode
  minWidth?: number  // 最小宽度百分比 (0-1)
  maxWidth?: number  // 最大宽度百分比 (0-1)
  padding?: number   // 内边距
  verticalAlign?: 'top' | 'center' | 'bottom'
  style?: React.CSSProperties
}

/**
 * 内容区域 — 宽度强制 ≥85% 屏幕
 *
 * 硬约束：
 * - 宽度范围: 85%-95% 屏幕
 * - 水平居中，但内容撑满
 * - 底部留 100px 给字幕
 */
export const ContentArea: React.FC<ContentAreaProps> = ({
  children,
  minWidth = tokens.layout.minContentWidth,
  maxWidth = tokens.layout.maxContentWidth,
  padding = tokens.spacing.page,
  verticalAlign = 'center',
  style,
}) => {
  const alignMap = {
    top: 'flex-start',
    center: 'center',
    bottom: 'flex-end',
  }

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: alignMap[verticalAlign],
        padding,
        paddingBottom: padding + tokens.layout.subtitleMargin, // 底部留白给字幕
        ...style,
      }}
    >
      <div
        style={{
          width: '100%',
          minWidth: `${minWidth * 100}%`,
          maxWidth: `${maxWidth * 100}%`,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {children}
      </div>
    </div>
  )
}

// ============================================================
// CoverMedia — 强制铺满的图片/视频
// ============================================================

interface CoverMediaProps {
  src: string
  type?: 'image' | 'video'
  style?: React.CSSProperties
}

/**
 * 强制铺满的媒体组件
 *
 * 硬约束：
 * - width: 100%, height: 100%
 * - objectFit: cover (裁剪填满)
 *
 * 所有图片/视频必须用此组件
 */
export const CoverMedia: React.FC<CoverMediaProps> = ({ src, type = 'image', style }) => {
  const baseStyle: React.CSSProperties = {
    position: 'absolute',
    inset: 0,
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    ...style,
  }

  if (type === 'video') {
    return <Video src={src} style={baseStyle} volume={0} />
  }
  return <Img src={src} style={baseStyle} />
}

// ============================================================
// DualLayerMedia — 双层结构 (模糊背景 + 清晰前景)
// ============================================================

interface DualLayerMediaProps {
  src: string
  type?: 'image' | 'video'
  foregroundFit?: 'contain' | 'cover'
  blurAmount?: number
  overlayOpacity?: number
}

/**
 * 双层媒体结构 — 解决非 16:9 素材的铺满问题
 *
 * 结构：
 * 1. 背景层：素材放大 + 模糊 (objectFit: cover)
 * 2. 遮罩层：轻微暗化提升可读性
 * 3. 前景层：清晰素材 (objectFit: contain)
 *
 * 用途：竖图、方图、截图等非 16:9 素材
 */
export const DualLayerMedia: React.FC<DualLayerMediaProps> = ({
  src,
  type = 'image',
  foregroundFit = 'contain',
  blurAmount = 30,
  overlayOpacity = 0.3,
}) => {
  const MediaComponent = type === 'video' ? Video : Img

  return (
    <FullBleed>
      {/* 背景层：放大 + 模糊 */}
      <MediaComponent
        src={src}
        style={{
          position: 'absolute',
          inset: '-20%', // 放大 140% 确保无边缘
          width: '140%',
          height: '140%',
          objectFit: 'cover',
          filter: `blur(${blurAmount}px)`,
        }}
        {...(type === 'video' ? { volume: 0 } : {})}
      />

      {/* 遮罩层：提升可读性 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `rgba(255,255,255,${overlayOpacity})`,
        }}
      />

      {/* 前景层：清晰素材 */}
      <MediaComponent
        src={src}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          objectFit: foregroundFit,
        }}
        {...(type === 'video' ? { volume: 0 } : {})}
      />
    </FullBleed>
  )
}

// ============================================================
// KenBurnsMedia — 带缩放动效的媒体
// ============================================================

interface KenBurnsConfig {
  startScale?: number
  endScale?: number
  focus?: 'center' | 'top' | 'bottom' | 'left' | 'right'
}

interface KenBurnsMediaProps {
  src: string
  type?: 'image' | 'video'
  config?: KenBurnsConfig
}

/**
 * Ken Burns 缩放动效媒体
 *
 * 硬约束：
 * - 始终铺满屏幕 (objectFit: cover)
 * - 缩放动效让静态图片更有生命力
 */
export const KenBurnsMedia: React.FC<KenBurnsMediaProps> = ({
  src,
  type = 'image',
  config = {},
}) => {
  const frame = useCurrentFrame()
  const { durationInFrames } = useVideoConfig()

  const { startScale = 1.0, endScale = 1.15, focus = 'center' } = config

  const progress = frame / durationInFrames
  const scale = interpolate(progress, [0, 1], [startScale, endScale])

  const originMap: Record<string, string> = {
    center: '50% 50%',
    top: '50% 0%',
    bottom: '50% 100%',
    left: '0% 50%',
    right: '100% 50%',
  }

  const MediaComponent = type === 'video' ? Video : Img

  return (
    <FullBleed>
      <MediaComponent
        src={src}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${scale})`,
          transformOrigin: originMap[focus],
        }}
        {...(type === 'video' ? { volume: 0 } : {})}
      />
    </FullBleed>
  )
}

// ============================================================
// 动画组件
// ============================================================

interface FadeInProps {
  children: React.ReactNode
  delay?: number
  duration?: number
  y?: number
}

/**
 * 淡入动画 — 带 translateY
 */
export const FadeIn: React.FC<FadeInProps> = ({
  children,
  delay = 0,
  duration = 25,
  y = 30,
}) => {
  const frame = useCurrentFrame()
  const progress = interpolate(frame - delay, [0, duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  })

  return (
    <div
      style={{
        opacity: progress,
        transform: `translateY(${interpolate(progress, [0, 1], [y, 0])}px)`,
      }}
    >
      {children}
    </div>
  )
}

interface SpringPopProps {
  children: React.ReactNode
  delay?: number
}

/**
 * 弹性缩放入场
 */
export const SpringPop: React.FC<SpringPopProps> = ({ children, delay = 0 }) => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()
  const progress = interpolate(frame - delay, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.back(1.5)),
  })

  return (
    <div style={{ transform: `scale(${progress})` }}>
      {children}
    </div>
  )
}

interface AnimatedCounterProps {
  value: number
  delay?: number
  duration?: number
  prefix?: string
  suffix?: string
  style?: React.CSSProperties
}

/**
 * 数字滚动动画
 */
export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  delay = 0,
  duration = 30,
  prefix = '',
  suffix = '',
  style,
}) => {
  const frame = useCurrentFrame()
  const progress = interpolate(frame - delay, [0, duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  })

  return (
    <span style={style}>
      {prefix}
      {Math.round(value * progress).toLocaleString()}
      {suffix}
    </span>
  )
}

// ============================================================
// 文字组件 — 预设样式
// ============================================================

interface TitleProps {
  children: React.ReactNode
  size?: 'hero' | 'large' | 'medium'
  color?: string
  style?: React.CSSProperties
}

/**
 * 标题组件 — 预设大字号
 */
export const Title: React.FC<TitleProps> = ({
  children,
  size = 'large',
  color = tokens.colors.text,
  style,
}) => {
  const sizeMap = {
    hero: tokens.fontSize.hero,
    large: tokens.fontSize.title,
    medium: tokens.fontSize.subtitle,
  }

  return (
    <div
      style={{
        fontSize: sizeMap[size],
        fontWeight: 800,
        color,
        letterSpacing: -2,
        lineHeight: 1.1,
        textAlign: 'center',
        ...style,
      }}
    >
      {children}
    </div>
  )
}

interface DataDisplayProps {
  value: string | number
  label?: string
  color?: string
  size?: 'large' | 'medium'
}

/**
 * 数据展示组件 — 大字号数字 + 说明
 */
export const DataDisplay: React.FC<DataDisplayProps> = ({
  value,
  label,
  color = tokens.colors.accent,
  size = 'large',
}) => {
  const fontSize = size === 'large' ? tokens.fontSize.dataLarge : tokens.fontSize.data

  return (
    <div style={{ textAlign: 'center' }}>
      <div
        style={{
          fontSize,
          fontWeight: 800,
          color,
          lineHeight: 1,
        }}
      >
        {value}
      </div>
      {label && (
        <div
          style={{
            fontSize: tokens.fontSize.caption,
            color: tokens.colors.textMuted,
            marginTop: 12,
          }}
        >
          {label}
        </div>
      )}
    </div>
  )
}

// ============================================================
// 布局验证工具 (开发时使用)
// ============================================================

interface DebugOverlayProps {
  show?: boolean
}

/**
 * 调试辅助层 — 显示边界和安全区
 *
 * 开发时开启，渲染时关闭
 */
export const DebugOverlay: React.FC<DebugOverlayProps> = ({ show = false }) => {
  if (!show) return null

  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
      {/* 屏幕边界 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          border: '4px solid red',
        }}
      />
      {/* 85% 内容区域 */}
      <div
        style={{
          position: 'absolute',
          top: '7.5%',
          left: '7.5%',
          right: '7.5%',
          bottom: '7.5%',
          border: '2px dashed blue',
        }}
      />
      {/* 底部字幕安全区 */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 100,
          background: 'rgba(255,0,0,0.2)',
        }}
      />
      {/* 标签 */}
      <div style={{ position: 'absolute', top: 10, left: 10, color: 'red', fontSize: 24 }}>
        DEBUG: Red=Screen Blue=85% Pink=Subtitle
      </div>
    </div>
  )
}

// ============================================================
// 导出常用字体
// ============================================================

export const font = '-apple-system, "SF Pro Display", "Noto Sans SC", "Helvetica Neue", sans-serif'
