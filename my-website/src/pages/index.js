import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import styles from './index.module.css';

export default function Home() {
  return (
    <Layout title="AI Native" description="Learn AI through a modern book-style website">
      <main className={styles.hero}>

        {/* IMAGE REMOVED */}
        {/* <div className={styles.left}>...</div> */}

        <div className={styles.rightCentered}>
          <div className={styles.badge}>
            AI-NATIVE BOOK SERIES
          </div>

          <h1 className={styles.title}>
            AI & Humanoid <span className={styles.gradient}> Robotics</span>
          </h1>

          <p className={styles.subtitle}>
            A modern, animated book-style learning experience where knowledge meets creativity.
          </p>

          <div className={styles.glassCard}>
            <p>✨ 100% Free Book</p>
            <p>📘 Beginner Friendly</p>
            <p>🤖 AI-Powered Explanations</p>
          </div>

          <div className={styles.buttons}>
            <Link className={styles.primaryButton} to="docs/chapter_01_physical_ai">
              Start Reading →
            </Link>
            <Link className={styles.secondaryButton} to="/docs/chapter_01_physical_ai">
              Explore Chapters 🚀
            </Link>
          </div>
        </div>

      </main>

      {/* PREMIUM SECTION (unchanged) */}
      <section className={styles.featuresSection}>
        <div className={styles.featuresContainer}>
          <h2 className={styles.sectionTitle}>Why This AI Book Stands Out?</h2>

          <div className={styles.featuresGrid}>
            <div className={styles.featureCard}>
              <h3>📘 Beginner Friendly</h3>
              <p>Concepts are simplified with visual examples and modern explanations.</p>
            </div>

            <div className={styles.featureCard}>
              <h3>🤖 Real Robotics</h3>
              <p>Learn how humanoid robots think, move, react and understand the world.</p>
            </div>

            <div className={styles.featureCard}>
              <h3>🎨 Modern Design</h3>
              <p>A clean, animated book-style interface designed for smooth learning.</p>
            </div>
          </div>
        </div>
      </section>

    </Layout>
  );
}
