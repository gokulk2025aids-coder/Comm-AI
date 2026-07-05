// Email Templates Library
const EMAIL_TEMPLATES = {
    "Apology": [
        {
            id: "apology_1",
            name: "General Apology",
            subject: "Sincere Apologies for [Issue]",
            body: `Dear [Recipient's Name],

I am writing to sincerely apologize for [specific issue/mistake]. I understand that this has caused [impact/inconvenience], and I take full responsibility for the situation.

[Explain what happened briefly and professionally]

To rectify this matter, I have already [actions taken]. Moving forward, I will [preventive measures] to ensure this does not happen again.

I truly value our professional relationship and appreciate your understanding in this matter. Please let me know if there is anything else I can do to make this right.

Thank you for your patience and continued support.

Best regards,
[Your Name]
[Your Position]`
        },
        {
            id: "apology_2",
            name: "Delayed Response Apology",
            subject: "Apologies for the Delayed Response",
            body: `Dear [Recipient's Name],

Please accept my sincere apologies for the delayed response to your email dated [date]. I understand the importance of timely communication, and I regret any inconvenience this delay may have caused.

[Brief explanation if appropriate, e.g., "I was dealing with an urgent matter" or "Your email was inadvertently overlooked"]

Regarding your inquiry about [topic], [provide the response/information they requested].

I have implemented measures to ensure more prompt responses in the future. Thank you for your patience and understanding.

Best regards,
[Your Name]`
        },
        {
            id: "apology_3",
            name: "Meeting Cancellation Apology",
            subject: "Apologies - Need to Reschedule Our Meeting",
            body: `Dear [Recipient's Name],

I sincerely apologize, but I need to reschedule our meeting originally planned for [date and time]. Due to [brief, professional reason], I am unable to attend at the scheduled time.

I understand this may cause inconvenience, and I truly appreciate your flexibility. Would any of the following times work better for you?

- [Option 1: Date and Time]
- [Option 2: Date and Time]
- [Option 3: Date and Time]

Alternatively, please suggest a time that suits your schedule, and I will do my best to accommodate.

Thank you for your understanding, and I look forward to our conversation.

Best regards,
[Your Name]`
        }
    ],
    "Request": [
        {
            id: "request_1",
            name: "Information Request",
            subject: "Request for Information Regarding [Topic]",
            body: `Dear [Recipient's Name],

I hope this email finds you well. I am writing to request information regarding [specific topic/matter].

Specifically, I would appreciate if you could provide:

1. [First item of information needed]
2. [Second item of information needed]
3. [Third item of information needed]

This information will help me [explain purpose/benefit]. If possible, I would appreciate receiving this by [date], as [reason for deadline if applicable].

Please let me know if you need any additional details or clarification regarding this request. I am happy to discuss this further at your convenience.

Thank you for your time and assistance.

Best regards,
[Your Name]
[Your Position]
[Contact Information]`
        },
        {
            id: "request_2",
            name: "Meeting Request",
            subject: "Request for Meeting - [Topic]",
            body: `Dear [Recipient's Name],

I hope you are doing well. I would like to request a meeting to discuss [topic/purpose of meeting].

The purpose of this meeting would be to:
- [Objective 1]
- [Objective 2]
- [Objective 3]

I estimate the meeting would take approximately [duration]. Would you be available during any of the following times?

- [Option 1: Date and Time]
- [Option 2: Date and Time]
- [Option 3: Date and Time]

If none of these times work for you, please let me know your availability, and I will be happy to adjust my schedule accordingly.

I look forward to our discussion.

Best regards,
[Your Name]`
        },
        {
            id: "request_3",
            name: "Document/File Request",
            subject: "Request for [Document/File Name]",
            body: `Dear [Recipient's Name],

I hope this message finds you well. I am writing to request [specific document/file] for [purpose/reason].

Could you please provide:
- [Specific document/file 1]
- [Specific document/file 2]
- [Any specific format or version requirements]

I need this information to [explain why you need it]. If possible, I would appreciate receiving these documents by [date] to ensure [reason for timeline].

Please let me know if you have any questions or if there are any forms I need to complete to facilitate this request.

Thank you for your assistance.

Best regards,
[Your Name]
[Your Position]`
        }
    ],
    "Follow-up": [
        {
            id: "followup_1",
            name: "General Follow-up",
            subject: "Following Up: [Original Subject]",
            body: `Dear [Recipient's Name],

I hope this email finds you well. I am following up on my previous email sent on [date] regarding [topic/subject].

I understand you have a busy schedule, and I wanted to check if you had the opportunity to review my request/proposal. 

To recap briefly:
[One or two sentence summary of your previous email]

If you need any additional information or clarification, please don't hesitate to let me know. I am happy to provide any details that would be helpful.

I look forward to hearing from you at your earliest convenience.

Best regards,
[Your Name]
[Your Position]
[Contact Information]`
        },
        {
            id: "followup_2",
            name: "Post-Meeting Follow-up",
            subject: "Thank You - Follow-up from Our Meeting",
            body: `Dear [Recipient's Name],

Thank you for taking the time to meet with me on [date]. I appreciated the opportunity to discuss [topic/subject].

As discussed, here is a summary of our key points and next steps:

Key Takeaways:
- [Point 1]
- [Point 2]
- [Point 3]

Action Items:
- [Your action item 1] - [Deadline]
- [Their action item 1] - [Deadline]
- [Shared action item] - [Deadline]

Please let me know if I missed anything or if you would like to add any points to this summary.

I look forward to our continued collaboration and will keep you updated on my progress.

Best regards,
[Your Name]`
        },
        {
            id: "followup_3",
            name: "Proposal Follow-up",
            subject: "Following Up on [Proposal/Project Name]",
            body: `Dear [Recipient's Name],

I hope you are doing well. I wanted to follow up on the proposal I submitted on [date] for [project/service name].

I am very enthusiastic about the opportunity to work with you on this project and believe we can deliver excellent results.

Have you had a chance to review the proposal? I would be happy to:
- Answer any questions you may have
- Provide additional information or clarification
- Discuss any modifications or adjustments
- Schedule a call to go over the details

Please let me know if there is anything I can do to assist in your decision-making process.

I look forward to hearing from you.

Best regards,
[Your Name]`
        }
    ],
    "Meeting": [
        {
            id: "meeting_1",
            name: "Meeting Invitation",
            subject: "Meeting Invitation: [Topic] - [Date]",
            body: `Dear [Recipient's Name],

I would like to invite you to a meeting to discuss [topic/purpose].

Meeting Details:
- Date: [Date]
- Time: [Time] ([Time Zone])
- Duration: [Estimated duration]
- Location: [Physical location or video conference link]

Agenda:
1. [Agenda item 1]
2. [Agenda item 2]
3. [Agenda item 3]
4. Q&A and next steps

Please confirm your attendance at your earliest convenience. If this time doesn't work for you, please let me know your availability, and I will do my best to reschedule.

[If applicable: I have attached relevant documents for your review prior to the meeting.]

Looking forward to our discussion.

Best regards,
[Your Name]`
        },
        {
            id: "meeting_2",
            name: "Meeting Confirmation",
            subject: "Confirming Our Meeting - [Date and Time]",
            body: `Dear [Recipient's Name],

This email is to confirm our upcoming meeting scheduled for:

Date: [Date]
Time: [Time] ([Time Zone])
Duration: [Duration]
Location/Link: [Location or video conference link]

Purpose: [Brief description of meeting purpose]

I have prepared [materials/agenda/presentation] for our discussion and look forward to a productive conversation.

Please let me know if you need to reschedule or if you have any questions before our meeting.

See you soon!

Best regards,
[Your Name]`
        },
        {
            id: "meeting_3",
            name: "Meeting Reminder",
            subject: "Reminder: Meeting Tomorrow - [Topic]",
            body: `Dear [Recipient's Name],

This is a friendly reminder about our meeting scheduled for tomorrow:

Date: [Date]
Time: [Time] ([Time Zone])
Duration: [Duration]
Location/Link: [Location or video conference link]

We will be discussing:
- [Topic 1]
- [Topic 2]
- [Topic 3]

[If applicable: Please review the attached documents before the meeting.]

If you need to reschedule or have any questions, please let me know as soon as possible.

Looking forward to speaking with you!

Best regards,
[Your Name]`
        }
    ],
    "Thank You": [
        {
            id: "thankyou_1",
            name: "General Thank You",
            subject: "Thank You - [Reason]",
            body: `Dear [Recipient's Name],

I wanted to take a moment to express my sincere gratitude for [specific reason - help, support, opportunity, etc.].

Your [assistance/guidance/support] with [specific situation] was invaluable and made a significant difference in [outcome/result]. I truly appreciate the time and effort you invested.

[Optional: Add specific details about how their help impacted you or the project]

Thank you once again for your [kindness/professionalism/expertise]. I look forward to the opportunity to work with you again in the future.

Best regards,
[Your Name]`
        },
        {
            id: "thankyou_2",
            name: "Post-Interview Thank You",
            subject: "Thank You - [Position] Interview",
            body: `Dear [Interviewer's Name],

Thank you for taking the time to meet with me today to discuss the [Position] role at [Company Name]. I enjoyed learning more about the position, the team, and the company's goals.

Our conversation reinforced my enthusiasm for this opportunity. I am particularly excited about [specific aspect discussed in the interview], and I believe my experience in [relevant skill/experience] would allow me to contribute effectively to your team.

I appreciate the insights you shared about [specific topic discussed], and I am confident that my skills in [relevant skills] align well with the role's requirements.

Please don't hesitate to contact me if you need any additional information. I look forward to hearing about the next steps in the process.

Thank you again for your time and consideration.

Best regards,
[Your Name]
[Phone Number]
[Email]`
        },
        {
            id: "thankyou_3",
            name: "Thank You for Business/Partnership",
            subject: "Thank You for Your Business",
            body: `Dear [Recipient's Name],

I wanted to personally thank you for choosing [Your Company] for [service/product/partnership]. We truly value your business and the trust you have placed in us.

It has been a pleasure working with you on [project/service], and we are committed to continuing to provide you with excellent service and support.

If you have any questions, concerns, or feedback, please don't hesitate to reach out. We are always here to help and continuously strive to improve our services.

Thank you once again for your partnership. We look forward to a long and successful relationship.

Best regards,
[Your Name]
[Your Position]
[Company Name]`
        }
    ],
    "Complaint Response": [
        {
            id: "complaint_1",
            name: "General Complaint Response",
            subject: "Re: Your Concern - [Issue]",
            body: `Dear [Recipient's Name],

Thank you for bringing this matter to our attention. I sincerely apologize for the inconvenience and frustration you have experienced regarding [specific issue].

I have thoroughly reviewed your concern, and I understand that [acknowledge their specific complaint]. This is not the level of service/quality we strive to provide, and I take full responsibility for addressing this situation.

Here is what I am doing to resolve this issue:

1. [Immediate action taken]
2. [Follow-up action]
3. [Preventive measure for the future]

[If applicable: As a gesture of goodwill, I would like to offer [compensation/solution].]

I will personally oversee the resolution of this matter and will keep you updated every step of the way. You can expect [specific timeline/next update].

Your feedback is invaluable in helping us improve our services. Thank you for your patience and for giving us the opportunity to make this right.

Please feel free to contact me directly at [your contact information] if you have any questions or concerns.

Best regards,
[Your Name]
[Your Position]
[Contact Information]`
        },
        {
            id: "complaint_2",
            name: "Service Issue Response",
            subject: "Our Apologies - Service Issue Resolution",
            body: `Dear [Recipient's Name],

I am writing in response to your recent complaint regarding [specific service issue]. First and foremost, I want to apologize for the poor experience you had with our service.

After investigating the matter, I have identified that [brief explanation of what went wrong]. This is unacceptable, and we are taking immediate steps to correct it.

Resolution Plan:
- [Immediate fix/solution]
- [Compensation if applicable]
- [Timeline for resolution]

Preventive Measures:
- [Action 1 to prevent recurrence]
- [Action 2 to prevent recurrence]

I will personally monitor this situation to ensure it is resolved to your satisfaction. I will follow up with you on [date] to confirm everything has been addressed.

We value your business and appreciate your patience as we work to make this right.

Sincerely,
[Your Name]
[Your Position]
[Direct Contact Information]`
        },
        {
            id: "complaint_3",
            name: "Product Quality Complaint Response",
            subject: "Re: Product Quality Concern - [Product Name]",
            body: `Dear [Recipient's Name],

Thank you for contacting us regarding the quality issue with [product name]. I sincerely apologize that the product did not meet your expectations or our quality standards.

I have reviewed your complaint about [specific issue], and I completely understand your disappointment. This is not representative of the quality we strive to deliver.

To resolve this matter, I would like to offer the following options:

Option 1: [Full refund/replacement]
Option 2: [Alternative solution]
Option 3: [Another alternative]

Please let me know which option you prefer, and I will process it immediately.

Additionally, I have forwarded your feedback to our quality control team to investigate how this occurred and to implement measures to prevent similar issues in the future.

Your satisfaction is our top priority. Please contact me directly at [contact information] if you have any questions or if there is anything else I can do to assist you.

Thank you for your patience and understanding.

Best regards,
[Your Name]
[Your Position]
[Company Name]
[Contact Information]`
        }
    ]
};

// Custom templates storage key
const CUSTOM_TEMPLATES_KEY = 'commai_custom_templates';

// Get custom templates from localStorage
function getCustomTemplates() {
    try {
        const stored = localStorage.getItem(CUSTOM_TEMPLATES_KEY);
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error('Error loading custom templates:', error);
        return [];
    }
}

// Save custom template
function saveCustomTemplate(template) {
    try {
        const customTemplates = getCustomTemplates();
        template.id = 'custom_' + Date.now();
        template.isCustom = true;
        customTemplates.push(template);
        localStorage.setItem(CUSTOM_TEMPLATES_KEY, JSON.stringify(customTemplates));
        return true;
    } catch (error) {
        console.error('Error saving custom template:', error);
        return false;
    }
}

// Delete custom template
function deleteCustomTemplate(templateId) {
    try {
        let customTemplates = getCustomTemplates();
        customTemplates = customTemplates.filter(t => t.id !== templateId);
        localStorage.setItem(CUSTOM_TEMPLATES_KEY, JSON.stringify(customTemplates));
        return true;
    } catch (error) {
        console.error('Error deleting custom template:', error);
        return false;
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EMAIL_TEMPLATES, getCustomTemplates, saveCustomTemplate, deleteCustomTemplate };
}
