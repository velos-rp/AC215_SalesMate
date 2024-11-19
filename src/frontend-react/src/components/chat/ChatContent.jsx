import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

// Styles
import styles from './ChatContent.module.css';

export function Markdown({
  children,
}) {
    return <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
            // Custom styling for elements
            a: ({ node, ...props }) => (
                <a className={styles.link} {...props} target="_blank" rel="noopener noreferrer" />
            ),
            ul: ({ node, ...props }) => (
                <ul className={styles.list} {...props} />
            ),
            ol: ({ node, ...props }) => (
                <ol className={styles.list} {...props} />
            ),
            blockquote: ({ node, ...props }) => (
                <blockquote className={styles.blockquote} {...props} />
            ),
        }}
    >
        {children}
    </ReactMarkdown>;
};

export function TypingIndicator() {
    return (
        <div className={styles.typingIndicator}>
            <span></span>
            <span></span>
            <span></span>
        </div>
    );
}