//! Sample crate that claude-kit's CI builds against the workspace lint configuration.

use std::fmt;

/// Errors raised while reading configuration.
#[derive(Debug, PartialEq, Eq)]
pub enum ConfigError {
    /// The value is not a port number between 0 and 65535.
    InvalidPort(String),
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidPort(value) => write!(f, "invalid port: {value}"),
        }
    }
}

impl std::error::Error for ConfigError {}

/// Parses a port number from configuration text.
pub fn parse_port(text: &str) -> Result<u16, ConfigError> {
    text.trim()
        .parse()
        .map_err(|_| ConfigError::InvalidPort(text.to_owned()))
}

#[cfg(test)]
mod tests {
    use super::{ConfigError, parse_port};

    #[test]
    fn parses_a_padded_port() {
        assert_eq!(parse_port(" 8080 ").unwrap(), 8080);
    }

    #[test]
    fn rejects_a_non_numeric_port() {
        assert_eq!(
            parse_port("http"),
            Err(ConfigError::InvalidPort("http".to_owned()))
        );
    }
}
