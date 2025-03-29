def generate_finished_message(display_name: str, picture_url: str, category: str = "quiz") -> dict:
    # Map ประเภทให้ชื่อภาษาไทย + อีโมจิ
    mode_titles = {
        "quiz": "🧠 คำถามแสนสนุก",
        "math": "➕ เกมบวกเลข",
        "memory": "🖼️ เกมจับคู่ภาพ",
        "vocab": "📚 คำศัพท์ภาษาอังกฤษ",
    }
    mode_title = mode_titles.get(category, "🎮 เกมสนุก")

    return {
        "type": "flex",
        "altText": "คุณตอบครบแล้ว!",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"เย้! ตอบครบแล้ว 🎉",
                        "align": "center",
                        "weight": "bold",
                        "color": "#FF6A4B",
                        "size": "xl"
                    },
                    {
                        "type": "text",
                        "text": f"ในหมวด {mode_title}",
                        "align": "center",
                        "size": "sm",
                        "color": "#6D4C41",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#FFECE8",
                "paddingAll": "md"
            },
            "hero": {
                "type": "image",
                "url": picture_url,
                "size": "full",
                "aspectRatio": "1:1",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": display_name,
                        "align": "center",
                        "weight": "bold",
                        "size": "lg",
                        "margin": "md",
                        "color": "#FF6A4B"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": "#FF6A4B"
                    },
                    {
                        "type": "text",
                        "text": "คำถามหมดแล้วสำหรับวันนี้",
                        "wrap": True,
                        "align": "center",
                        "margin": "lg",
                        "size": "md",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "กรุณากลับมาใหม่ในวันพรุ่งนี้นะค้าบ 😊",
                        "wrap": True,
                        "align": "center",
                        "margin": "md",
                        "size": "sm",
                        "color": "#444444"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "ขอบคุณที่ร่วมสนุก!",
                                "size": "sm",
                                "color": "#FF6A4B",
                                "align": "center",
                                "margin": "md",
                                "style": "italic"
                            }
                        ],
                        "margin": "lg"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": "#FFFFFF"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "ดูคะแนนของฉัน",
                            "text": "ดูคะแนน"
                        },
                        "style": "primary",
                        "color": "#FF6A4B"
                    }
                ],
                "paddingAll": "md"
            }
        }
    }