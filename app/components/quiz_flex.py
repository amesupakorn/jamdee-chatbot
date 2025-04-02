
def generate_quiz_flex(question_data, header_title="🧠 คำถามแสนสนุก"):
    """
    question_data = {
        "question": str,
        "choices": [str, str, ...],
        "answer": str,
        "image_url": str
    }
    """
    choice_buttons = []
    for i, c in enumerate(question_data["choices"]):
        choice_buttons.append({
            "type": "button",
            "action": {
                "type": "postback", 
                "label": c,
                "data": f"answer={c}|correct={question_data['answer']}|question={question_data['id']}|mode={question_data.get('mode', 'quiz')}"     
            },
            "style": "primary",
            "color": "#FF6A4B",
            "height": "sm",
            "margin": "md"
        })
        if i < len(question_data["choices"]) - 1:
            choice_buttons.append({"type": "separator", "margin": "sm"})

    return {
        "type": "flex",
        "altText": "คำถามมาแล้ว!",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": header_title,
                        "weight": "bold",
                        "size": "xl",
                        "align": "center",
                        "color": "#FF6A4B"
                    }
                ],
                "backgroundColor": "#FFECE8",
                "paddingAll": "lg"
            },
            "hero": {
                "type": "image",
                "url": question_data.get("image_url", "https://i.imgur.com/UePbdph.png"),
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": question_data["question"],
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True,
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "เลือกคำตอบที่ถูกต้อง",
                        "size": "sm",
                        "color": "#6D4C41",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": choice_buttons,
                        "margin": "xl"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": "#FFF3F0"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "ตอบคำถามเพื่อสะสมคะแนน",
                        "size": "xs",
                        "color": "#AAAAAA",
                        "align": "center"
                    }
                ],
                "paddingAll": "lg",
                "backgroundColor": "#FFF3F0"
            }
        }
    }