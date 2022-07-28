<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress' );

/** MySQL database username */
define( 'DB_USER', 'wordpressuser232' );

/** MySQL database password */
define( 'DB_PASSWORD', 'galoshes' );

/** MySQL hostname */
define( 'DB_HOST', '172.17.0.3' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define('AUTH_KEY',         'vCZ!A7MeHF+[S]>MQ_KGMx=([49hvGW36cb[bwhH-pMUKi(>S9;M-J_vVK;4T$J{');
define('SECURE_AUTH_KEY',  's-QxHiZ|DX&$ei$qsp`{(kdWw59c*+xXEM1ab_S4g}t 5s2ZF%P??j@QXHZu]hn0');
define('LOGGED_IN_KEY',    '#L$2RHN?HZwU>TPXz;gcU<U$@=PKse_r,7N^#TaEFB-q~Hccwr0KvfFx:?6r[!s@');
define('NONCE_KEY',        '6gUhDyP1`MJeP,?2&<w8G(YUgK#~,@?Mwc|xG~<0}s}-]!ysq9N{*!EAF?{Q,iYI');
define('AUTH_SALT',        '+G(&4EZd4>[[M!^A|+jm+.;$lALN!w{q?a-0oYV(V;J$`T!KU@&mQqE{gxmA@8P)');
define('SECURE_AUTH_SALT', '}y(HD?o,]7/i%~nBw-|l:8BDU#3nBAc}j4C?.bo#5jx2hl+~*B`!t0OQO+6c*7%8');
define('LOGGED_IN_SALT',   '}?Gf?gl(i*c7B<jYL|eV~/n4|Au>Qq<]L:z6GxT(>++/bLKU$&(*&qd&X1}g[{{o');
define('NONCE_SALT',       'lzbPSq[r<&j|2NdMqlFO;+06{|cV/%:>+Hcq%^xo/~c3y%w-}0G`?#e:3xU9RK3!');

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', false );

/* Add any custom values between this line and the "stop editing" line. */

/** Disable saving revisions */
define( 'WP_POST_REVISIONS', false );

/** Use the Queen's English */
define('WPLANG', 'en_GB');


/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
        define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';