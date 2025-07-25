plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.9.0"
    id("org.jetbrains.intellij") version "1.16.0"
}

group = "com.devex"
version = "0.1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.15.2")
    testImplementation("org.jetbrains.kotlin:kotlin-test")
}

intellij {
    version.set("2023.2.5")
    type.set("IC")
    plugins.set(listOf("com.intellij.java", "Git4Idea"))
}

tasks {
    withType<JavaCompile> {
        sourceCompatibility = "17"
        targetCompatibility = "17"
    }
    withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
        kotlinOptions.jvmTarget = "17"
    }
    
    patchPluginXml {
        sinceBuild.set("232")
        untilBuild.set("242.*")
    }
}
