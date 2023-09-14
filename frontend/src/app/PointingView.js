'use client'

export default function PointingView({isVisible}) {
    return <div is_visible={isVisible.toString()}>This is the pointing view</div>
}